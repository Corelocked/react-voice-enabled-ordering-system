from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, current_user
import pandas as pd
from fuzzywuzzy import fuzz, process
import nltk
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
        print("Frequent words:", frequent_words)  # Debugging statement to check frequent words
        return inquiries_dict, frequent_words
    except Exception as e:
        print(f"Error loading inquiries: {e}")
        return {}, set()

# Store the inquiry responses from CSV
inquiry_responses, frequent_words = load_inquiries('inquiries.csv')

# Ensure frequent_words is correctly initialized before using it in match_inquiry function
if not frequent_words:
    print("Error: frequent_words is empty or not loaded properly.")

# Function to perform fuzzy matching between user input and CSV questions
def match_inquiry(user_input):
    # Preprocess the user input
    if not frequent_words:
        return "Error: Frequent words not loaded properly"
    
    user_input_processed = ' '.join([word for word in preprocess_text(user_input) if word not in frequent_words])
    
    # Perform fuzzy matching
    best_match, score = process.extractOne(user_input_processed.lower(), inquiry_responses.keys(), scorer=fuzz.token_set_ratio)
    if score >= 75:  # Adjust threshold for stricter matching
        return inquiry_responses[best_match]
    else:
        return None


# Define the intents and corresponding keywords
INTENT_KEYWORDS = {
    "Room Service Order": ["order", "food", "room service", "meal", "menu", "snack", "drink", "coffee", "tea", "breakfast", "lunch", "dinner"],
    "Amenities Request": ["towel", "pillows", "extra blanket", "bathroom", "toiletries", "shampoo", "soap", "hair dryer", "robe"],
    "Food Inquiry": ["ice cream", "food", "meal", "snack", "dessert", "order food", "can I get food", "menu", "available food", "specials", "what's for dinner"],
    "Feedback or Complaint": ["complaint", "feedback", "issue", "problem", "cold", "hot", "broken", "not working", "too loud", "uncomfortable"],
    "Reservation Request": ["reserve", "booking", "reservation", "room", "book a room", "availability", "room booking", "confirm reservation"],
    "Check-In/Check-Out Request": ["check-in", "check-out", "checkin", "checkout", "time", "arrivals", "departure", "when is check-in", "when is check-out"],
    "Parking Inquiry": ["parking", "space", "available", "park", "parking fee", "parking available", "where to park"],
    "General Inquiry": ["what", "how", "where", "is", "can", "please", "help", "do you have", "what time", "how much", "how to", "how does it work"],
    "Yes/No Response": ["yes", "no", "yeah", "nope", "yup", "nah", "correct", "incorrect", "sure", "no thanks", "maybe"],
    "Greeting": ["hi", "hello", "hey", "good morning", "good afternoon", "good evening", "how are you", "good day", "welcome", "greetings"],
    "Cancellation or Modification": ["cancel", "modify", "change", "alter", "adjust", "reschedule", "cancel reservation", "change booking"],
    "Special Request": ["special request", "extra service", "personal request", "room preference", "need help", "special arrangement"],
    "Maintenance Request": ["broken", "repair", "leak", "damaged", "fix", "maintenance", "malfunction", "problem with", "faulty"],
    "Housekeeping Request": ["cleaning", "housekeeping", "tidy up", "make the bed", "room cleaning", "change the sheets", "vacuum", "clean the bathroom"],
    "Payment/Invoice Request": ["bill", "invoice", "payment", "charge", "receipt", "how much", "total cost", "pay for", "room charges", "bill for the stay"],
    "Staff Assistance Request": ["help", "assist", "staff", "can you help", "please assist", "need assistance", "staff available"],
    "Lost and Found": ["lost", "found", "missing", "lost item", "found item", "where is my", "where did I leave"],
    "Local Information Request": ["nearby", "attractions", "restaurant", "tourist spots", "local", "near", "places to visit", "local area", "activities nearby"],
    "Event or Conference Room": ["conference room", "meeting room", "event space", "book a conference room", "reserve a meeting room", "event booking"]
}

# Define the responses for each intent
INTENT_RESPONSES = {
    "Room Service Order": "Thank you for your order! Your food will be delivered shortly.",
    "Amenities Request": "Your request for additional amenities has been noted and will be sent to your room soon.",
    "Food Inquiry": "Ice cream sounds great! Let me place that order for you right away. What flavor would you like?",
    "Feedback or Complaint": "We're sorry to hear that. Could you please provide more details about the issue?",
    "Reservation Request": "Your reservation request is being processed. We'll confirm your booking shortly.",
    "Check-In/Check-Out Request": "Your check-in/check-out request has been noted. Please proceed to the front desk for further assistance.",
    "Parking Inquiry": "Yes, parking is available for guests. There is a daily parking fee of $10.",
    "General Inquiry": "How can I assist you today? Please feel free to ask any questions you may have.",
    "Yes/No Response": "Thank you for your response!",
    "Greeting": "Hello! How can I assist you today?",
    "Cancellation or Modification": "Your request to cancel or modify the reservation will be processed shortly.",
    "Special Request": "We will take care of your special request. Please let us know if there's anything else you need.",
    "Maintenance Request": "We're sorry to hear that! Our maintenance team will attend to the issue shortly.",
    "Housekeeping Request": "Housekeeping will be sent to your room to take care of your request.",
    "Payment/Invoice Request": "Your bill will be provided shortly. Let us know if you need any further assistance with the payment.",
    "Staff Assistance Request": "Our staff is here to help. How can we assist you today?",
    "Lost and Found": "Please provide details about the item you lost, and we'll check if it has been found.",
    "Local Information Request": "I can provide information about local attractions. What kind of activities are you interested in?",
    "Event or Conference Room": "I will reserve a conference room for you. Could you please provide more details about the event?"
}

# Function to determine intent based on keywords
def determine_intent(user_input):
    user_input = user_input.lower()

    # First, try to match the user input with the inquiry responses
    inquiry_response = match_inquiry(user_input)
    if inquiry_response:
        return "Inquiry", inquiry_response

    # Check for greeting keywords
    if any(keyword in user_input for keyword in INTENT_KEYWORDS["Greeting"]):
        return "Greeting", "Hello! How can I assist you today?"

    # Check for yes/no keywords
    if any(keyword in user_input for keyword in INTENT_KEYWORDS["Yes/No Response"]):
        return "Yes/No", "Thank you for your response!"

    # Check for feedback or complaint specifically
    if any(keyword in user_input for keyword in INTENT_KEYWORDS["Feedback or Complaint"]):
        return "Feedback or Complaint", "We're sorry to hear that. Could you please provide more details about the issue?"

    # Check for keyword matches for predefined intents
    for intent, keywords in INTENT_KEYWORDS.items():
        if intent not in ["Greeting", "Yes/No Response", "Feedback or Complaint"] and any(keyword in user_input for keyword in keywords):
            return intent, INTENT_RESPONSES.get(intent, "I'm sorry, I didn't quite understand your request.")

    return "Unknown", "I'm sorry, I didn't quite understand your request."

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
