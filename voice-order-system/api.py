from flask import Flask, request, jsonify
from flask_cors import CORS
from transcribe import record_and_transcribe
from intent_recognizer import recognize_intent
from sentiment_analysis import analyze_sentiment
from user_log import log_interaction, log_feedback
import joblib
import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

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

@app.route('/api/voice-order', methods=['POST'])
def voice_order():
    user_input = request.json.get('input')
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    try:
        intent = recognize_intent(user_input)
        sentiment, score = analyze_sentiment(user_input)
        response = handle_intent(intent, sentiment, user_input)  # Pass user_input here

        # Log the interaction
        log_interaction(user_input, intent, sentiment, response)

        # Create response data
        response_data = {
            "response": response,
            "intent": intent,
            "sentiment": sentiment,
            "score": score
        }
        print("Response Data:", response_data)
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
def feedback():
    user_feedback = request.json.get('feedback')
    if not user_feedback:
        return jsonify({"error": "No feedback provided"}), 400

    # Log feedback
    log_feedback(user_feedback)
    return jsonify({"message": "Thank you for your feedback!"}), 200

@app.route('/api/user/preferences', methods=['GET'])
@login_required
def get_user_preferences():
    user_id = current_user.id
    user = User.query.get(user_id)
    return jsonify({"favorite_foods": user.favorite_foods.split(',') if user.favorite_foods else []})

def handle_intent(intent, sentiment, user_input):
    positive_response = "Thank you for your request! "
    neutral_response = "I see. "
    negative_response = "I'm sorry to hear that. "

    if intent == "Room Service Order":
        return positive_response + "Your order has been received. We'll prepare your food shortly."

    elif intent == "Amenities Request":
        return positive_response + "Your request for additional amenities has been noted. We'll send them to your room soon."

    elif intent == "Inquiry":
        return neutral_response + "Could you please specify what information you would like?"

    elif intent == "Feedback or Complaint":
        return negative_response + "We appreciate your feedback. Can you provide more details about the issue?"

    elif intent == "Reservation Request":
        return positive_response + "Your reservation request is being processed. We'll confirm your booking shortly."

    elif intent == "Check-In/Check-Out Request":
        return positive_response + "Your check-in/check-out request has been noted. Please proceed to the front desk for further assistance."

    elif intent is None or intent == "Unknown":
        # If intent is not recognized or ambiguous, ask for clarification
        return neutral_response + "I'm not quite sure how to help with that. Could you clarify if you're looking to order food, request amenities, or something else?"

    else:
        return "I'm not sure how to help with that. You can ask me to place an order, request amenities, or ask for information."
    

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
