from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import defaultdict
from transcribe import record_and_transcribe  # Assuming you have these functions defined
from intent_recognizer import recognize_intent  # Assuming you have these functions defined
from sentiment_analysis import analyze_sentiment  # Assuming you have these functions defined
from user_log import log_interaction  # Assuming you have these functions defined
import joblib

app = Flask(__name__)
CORS(app)

# Load model and vectorizer once when the app starts
model = joblib.load('models/logistic_regression_model.joblib')
vectorizer = joblib.load('models/count_vectorizer.joblib')

# Dictionary to hold user context
user_context = defaultdict(dict)

@app.route('/api/voice-order', methods=['POST'])
def voice_order():
    user_id = request.json.get('user_id', 'default_user')  # Get user ID for context
    user_input = request.json.get('input')
    
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    try:
        # Get the previous context for the user
        previous_order = user_context[user_id].get('last_order', None)
        
        intent = recognize_intent(user_input)
        sentiment, score = analyze_sentiment(user_input)  # Get both sentiment label and score

        # Update user context based on intent
        update_user_context(user_id, intent, user_input)

        response = handle_intent(intent, sentiment, previous_order)  # Pass previous order to context-aware response

        # Log the interaction
        log_interaction(user_input, intent, sentiment, response)

        # Create response data
        response_data = {
            "response": response,
            "intent": intent,
            "sentiment": sentiment,
            "score": score
        }
        print("Response Data:", response_data)  # Log response data for debugging
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def update_user_context(user_id, intent, user_input):
    if intent in ["Room Service Order", "Order Food"]:
        # Store the last order for context
        user_context[user_id]['last_order'] = user_input

def handle_intent(intent, sentiment, previous_order):
    # Define base responses based on sentiment
    positive_response = "Thank you for your request! "
    neutral_response = "I see. "
    negative_response = "I'm sorry to hear that. "

    # Handle intents with context-aware responses
    if intent in ["Room Service Order", "Order Food"]:
        if previous_order:
            return positive_response + f"Your previous order was '{previous_order}'. This new order has been received, and we'll prepare your food shortly."
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

    else:
        return "I'm not sure how to help with that. You can ask me to place an order, request amenities, or ask for information."

if __name__ == "__main__":
    app.run(debug=True)
