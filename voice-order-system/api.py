from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, current_user
import pandas as pd
from fuzzywuzzy import fuzz, process
import nltk
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter

app = Flask(__name__)
CORS(app)

# Set a secret key for session management
app.secret_key = os.getenv("SECRET_KEY", "your_default_secret_key_here")

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    favorite_foods = db.Column(db.String(200))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Load inquiries and responses from CSV
stop_words = set(stopwords.words('english'))

# Function to preprocess text by removing stopwords
def preprocess_text(text):
    tokens = word_tokenize(text.lower())  # Tokenize and convert to lowercase
    return [word for word in tokens if word.isalpha() and word not in stop_words]

# Function to identify frequently occurring words in the CSV questions
def get_frequent_words(df, threshold=5):
    word_count = Counter()
    
    for question in df['Question']:
        words = preprocess_text(question)
        word_count.update(words)

    # Filter out words that occur more than a certain threshold
    frequent_words = {word for word, count in word_count.items() if count >= threshold}
    return frequent_words

# Load and preprocess inquiries from CSV
def load_inquiries(file_path):
    try:
        df = pd.read_csv(file_path)
        df['Question'] = df['Question'].str.strip()  # Clean up any extra spaces

        # Preprocess the questions and remove frequent words
        frequent_words = get_frequent_words(df)
        df['Processed Question'] = df['Question'].apply(lambda x: ' '.join([word for word in preprocess_text(x) if word not in frequent_words]))

        inquiries_dict = dict(zip(df['Processed Question'].str.lower(), df['Response']))
        return inquiries_dict, frequent_words
    except Exception as e:
        print(f"Error loading inquiries: {e}")
        return {}, set()

# Store the inquiry responses from CSV
inquiry_responses, frequent_words = load_inquiries('inquiries.csv')

# Function to perform fuzzy matching between user input and CSV questions
def match_inquiry(user_input):
    # Preprocess the user input
    user_input_processed = ' '.join([word for word in preprocess_text(user_input) if word not in frequent_words])
    
    # Perform fuzzy matching
    best_match, score = process.extractOne(user_input_processed.lower(), inquiry_responses.keys(), scorer=fuzz.token_set_ratio)
    if score >= 75:  # Adjust threshold for stricter matching
        return inquiry_responses[best_match]
    else:
        return None

# Function to determine intent based on keywords
def determine_intent(user_input):
    user_input = user_input.lower()

    # First, try to match the user input with the inquiry responses
    inquiry_response = match_inquiry(user_input)
    if inquiry_response:
        return "Inquiry", inquiry_response

    # Define the intents and corresponding keywords
    INTENT_KEYWORDS = {
        "Room Service Order": ["order", "food", "room service", "meal"],
        "Amenities Request": ["amenities", "towel", "extra", "pillows", "blanket"],
        "Feedback or Complaint": ["complaint", "feedback", "issue", "problem"],
        "Reservation Request": ["reserve", "booking", "reservation", "room"],
        "Check-In/Check-Out Request": ["check-in", "check-out", "checkin", "checkout", "time"],
        "Parking Inquiry": ["parking", "space", "available", "park"]  # Added parking intent
    }

    # Check for keyword matches for predefined intents
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in user_input for keyword in keywords):
            return intent, INTENT_RESPONSES.get(intent, "I'm sorry, I didn't quite understand your request.")

    return "Unknown", "I'm sorry, I didn't quite understand your request."

# Define the responses for each intent
INTENT_RESPONSES = {
    "Room Service Order": "Thank you for your order! Your food will be delivered shortly.",
    "Amenities Request": "Your request for additional amenities has been noted and will be sent to your room soon.",
    "Feedback or Complaint": "We're sorry to hear that. Could you please provide more details about the issue?",
    "Reservation Request": "Your reservation request is being processed. We'll confirm your booking shortly.",
    "Check-In/Check-Out Request": "Your check-in/check-out request has been noted. Please proceed to the front desk for further assistance.",
    "Parking Inquiry": "Yes, parking is available for guests. There is a daily parking fee of $10."  # Added parking response
}

# Function to handle user input and generate a response
def handle_user_input(user_input):
    intent, response = determine_intent(user_input)
    return response

@app.route('/api/voice-order', methods=['POST'])
def voice_order():
    user_input = request.json.get('input')
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    response = handle_user_input(user_input)
    
    # Create response data
    response_data = {
        "response": response
    }
    return jsonify(response_data)

@app.route('/api/feedback', methods=['POST'])
def feedback():
    user_feedback = request.json.get('feedback')
    if not user_feedback:
        return jsonify({"error": "No feedback provided"}), 400

    # Log feedback here (implement logging if needed)
    return jsonify({"message": "Thank you for your feedback!"}), 200

@app.route('/api/user/preferences', methods=['GET'])
@login_required
def get_user_preferences():
    user_id = current_user.id
    user = User.query.get(user_id)
    return jsonify({"favorite_foods": user.favorite_foods.split(',') if user.favorite_foods else []})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
