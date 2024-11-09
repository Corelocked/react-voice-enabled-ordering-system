from flask import Flask, request, jsonify
from flask_cors import CORS
from fuzzywuzzy import process, fuzz
import fuzzywuzzy
import pandas as pd
import re
import joblib
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, current_user

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

# Load model and vectorizer once when the app starts
try:
    model = joblib.load('models/logistic_regression_model.joblib')
    vectorizer = joblib.load('models/count_vectorizer.joblib')
except Exception as e:
    print("Error loading model or vectorizer:", e)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Load inquiry responses from CSV
def load_inquiry_responses(file_path):
    try:
        df = pd.read_csv(file_path)
        inquiries_dict = dict(zip(df['Question'].str.lower(), df['Response']))
        return inquiries_dict
    except Exception as e:
        print(f"Error loading inquiries: {e}")
        return {}

# Store the inquiry responses
inquiry_responses = load_inquiry_responses('inquiries.csv')

def handle_inquiry(user_input):
    inquiry_keys = list(inquiry_responses.keys())
    print(f"Inquiry Keys: {inquiry_keys}")  # Debug print

    if not inquiry_keys:
        return "No inquiries loaded. Please check the CSV file."

    try:
        # Use the fuzz scorer for fuzzy matching
        best_match, score = process.extractOne(user_input.lower(), inquiry_keys, scorer=fuzz.token_set_ratio)
    except Exception as e:
        print(f"Error in fuzzy matching: {e}")
        return "There was an error processing your inquiry."

    # Continue with your logic...
    if score >= 60:  # Adjust threshold as needed
        return inquiry_responses[best_match]
    
    # Check for keywords using regex for common inquiries
    keywords = {
        "pool hours": "What are the pool hours?",
        "breakfast included": "Is breakfast included in my booking?",
        "check-in": "What time is check-in and check-out?",
        "late checkout": "Do you offer late checkout?",
        "nearest atm": "Where is the nearest ATM?",
        "parking": "Is there parking available at the hotel?", 
        "parking space": "Is there parking available at the hotel?", 
        "where can i park": "Where can I find parking?",
        "how to park": "How can I park my car?",
        # Add more keywords and corresponding inquiries as needed
    }

    # First check for direct keyword matches
    for keyword, inquiry in keywords.items():
        if re.search(re.escape(keyword), user_input.lower()):
            return inquiry_responses.get(inquiry.lower(), "I couldn't find the answer to that inquiry.")

    # Fallback to fuzzy matching if no keyword matches
    return "I'm not quite sure how to help with that. Could you clarify your question?"

def handle_intent(intent, sentiment, user_input):
    positive_response = "Thank you for your request! "
    neutral_response = "I see. "
    negative_response = "I'm sorry to hear that. "

    if intent == "Room Service Order":
        return positive_response + "Your order has been received. We'll prepare your food shortly."

    elif intent == "Amenities Request":
        return positive_response + "Your request for additional amenities has been noted. We'll send them to your room soon."

    elif intent == "Inquiry":
        return handle_inquiry(user_input)

    elif intent == "Feedback or Complaint":
        return negative_response + "We appreciate your feedback. Can you provide more details about the issue?"

    elif intent == "Reservation Request":
        return positive_response + "Your reservation request is being processed. We'll confirm your booking shortly."

    elif intent == "Check-In/Check-Out Request":
        return positive_response + "Your check-in/check-out request has been noted. Please proceed to the front desk for further assistance."

    elif intent is None or intent == "Unknown":
        return neutral_response + "I'm not quite sure how to help with that. Could you clarify if you're looking to order food, request amenities, or something else?"

    else:
        return "I'm not sure how to help with that. You can ask me to place an order, request amenities, or ask for information."

@app.route('/api/voice-order', methods=['POST'])
def voice_order():
    user_input = request.json.get('input')
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    # Handle inquiry using the new function
    response = handle_inquiry(user_input)
    
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
