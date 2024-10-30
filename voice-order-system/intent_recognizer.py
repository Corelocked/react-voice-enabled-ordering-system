import re

def recognize_intent(text):
    # Define keywords and their corresponding intents
    intent_patterns = {
        "Room Service Order": r"\b(order|bring|can I get|want|could I have|I'd like|ice cream|pizza|sandwich|burger|food)\b",
        "Amenities Request": r"\b(need|request|extra|more|get me|can I have|could you provide|send me|bring me)\b",
        "Inquiry": r"\b(time|when|where|how|can I|what time|tell me about|information)\b",
        "Feedback or Complaint": r"\b(not happy|complaint|problem|issue|unsatisfied|unhappy|bad experience|dissatisfied)\b",
        "Reservation Request": r"\b(book|reserve|reservation|table|booking|reserve a spot|make a reservation)\b",
        "Check-In/Check-Out Request": r"\b(check-in|check out|early check-out|late check-in|early check|late checkout)\b"
    }

    # Iterate through patterns to find a match
    for intent, pattern in intent_patterns.items():
        if re.search(pattern, text.lower()):
            return intent

    # If no patterns match, return Unknown Intent
    return "Unknown Intent"
