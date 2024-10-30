import pyttsx3
from transcribe import record_and_transcribe
from intent_recognizer import recognize_intent
from sentiment_analysis import analyze_sentiment
from user_log import log_interaction

# Initialize text-to-speech engine
engine = pyttsx3.init()

def speak(response):
    engine.say(response)
    engine.runAndWait()

# Define functions to handle each intent with personalized responses
def handle_room_service_order(sentiment):
    if sentiment == "Positive":
        response = "I'd be delighted to place that order for you!"
    elif sentiment == "Negative":
        response = "I'm sorry if there's been an issue. I'll make sure to get your order just right."
    else:
        response = "Processing your order now."
    print(response)
    speak(response)
    return response

def handle_amenities_request(sentiment):
    if sentiment == "Positive":
        response = "Sure, I'll get those amenities for you right away!"
    elif sentiment == "Negative":
        response = "I apologize for any inconvenience. I'll arrange the amenities as quickly as possible."
    else:
        response = "Arranging your requested amenities."
    print(response)
    speak(response)
    return response

def handle_inquiry(sentiment):
    if sentiment == "Positive":
        response = "I'd be happy to answer that for you!"
    elif sentiment == "Negative":
        response = "I understand your concern. Let me provide the information you need."
    else:
        response = "Here’s the information you requested."
    print(response)
    speak(response)
    return response

def handle_feedback_complaint(sentiment):
    response = "Thank you for your feedback. I’m here to help resolve any issues."
    if sentiment == "Negative":
        response += " I'm very sorry to hear that. I'll make sure your concerns are addressed."
    print(response)
    speak(response)
    return response

def handle_reservation_request(sentiment):
    if sentiment == "Positive":
        response = "Reservation confirmed! I'll take care of it right away."
    elif sentiment == "Negative":
        response = "Sorry if there was any inconvenience with reservations. Let’s get this booked for you."
    else:
        response = "Your reservation is being made."
    print(response)
    speak(response)
    return response

def handle_checkin_checkout_request(sentiment):
    if sentiment == "Positive":
        response = "No problem! Let me update your check-in/check-out as requested."
    elif sentiment == "Negative":
        response = "I understand it may be important to adjust your schedule. I'll make the change."
    else:
        response = "Updating your check-in/check-out details."
    print(response)
    speak(response)
    return response

def handle_cancellation_request(sentiment):
    response = "Processing your cancellation request."
    if sentiment == "Negative":
        response += " I'm sorry to hear that you're canceling. Please let me know if there's anything we can do."
    print(response)
    speak(response)
    return response

def handle_extend_stay_request(sentiment):
    response = "Your request to extend your stay is being processed."
    if sentiment == "Negative":
        response += " I apologize for any issues with your current stay."
    print(response)
    speak(response)
    return response

def handle_room_upgrade_request(sentiment):
    response = "I'll check availability for a room upgrade."
    if sentiment == "Negative":
        response += " I'm sorry if your current room didn't meet your expectations."
    print(response)
    speak(response)
    return response

def handle_billing_inquiry(sentiment):
    response = "Let me pull up your billing information."
    if sentiment == "Negative":
        response += " I'm here to help resolve any billing issues."
    print(response)
    speak(response)
    return response

def handle_unknown_intent(sentiment):
    response = "Sorry, I didn't understand that request."
    if sentiment == "Negative":
        response += " I apologize for the confusion. Could you please clarify your request?"
    print(response)
    speak(response)
    return response

# Main function with error handling
def main():
    print("Voice-Activated Order System Initialized.")
    while True:
        print("Listening...")
        user_input = ""  # Initialize user_input
        try:
            user_input = record_and_transcribe()
            print("You said:", user_input)

            # Recognize intent and analyze sentiment
            intent = recognize_intent(user_input)
            sentiment = analyze_sentiment(user_input)

            # Call appropriate handler and log interaction
            if intent == "Room Service Order":
                response = handle_room_service_order(sentiment)
            elif intent == "Amenities Request":
                response = handle_amenities_request(sentiment)
            elif intent == "Inquiry":
                response = handle_inquiry(sentiment)
            elif intent == "Feedback or Complaint":
                response = handle_feedback_complaint(sentiment)
            elif intent == "Reservation Request":
                response = handle_reservation_request(sentiment)
            elif intent == "Check-In/Check-Out Request":
                response = handle_checkin_checkout_request(sentiment)
            elif intent == "Cancellation Request":
                response = handle_cancellation_request(sentiment)
            elif intent == "Extend Stay Request":
                response = handle_extend_stay_request(sentiment)
            elif intent == "Room Upgrade Request":
                response = handle_room_upgrade_request(sentiment)
            elif intent == "Billing Inquiry":
                response = handle_billing_inquiry(sentiment)
            else:
                response = handle_unknown_intent(sentiment)

            # Log the interaction
            log_interaction(user_input, intent, sentiment, response)

        except Exception as e:
            print(f"An error occurred: {e}")
            log_interaction(user_input, "Error", "Unknown", "Error processing request")

if __name__ == "__main__":
    main()
