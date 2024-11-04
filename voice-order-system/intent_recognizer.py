import re

def recognize_intent(text):
    # Normalize text for consistency
    text = text.lower().strip()
    
    # Define keywords and their corresponding intents with improved regex patterns
    intent_patterns = {
        "Room Service Order": r"\b(?:order|bring|get|want|have|could I have|I'd like|please bring|ice cream|pizza|sandwich|burger|food|dinner|meal)\b",
        "Amenities Request": r"\b(?:need|request|extra|more|get me|can I have|could you provide|send me|bring me|add)\b",
        "Inquiry": r"\b(?:time|when|where|how|what|tell me about|information|details)\b",
        "Feedback or Complaint": r"\b(?:not happy|complaint|problem|issue|unsatisfied|unhappy|bad experience|dissatisfied|issue|concern)\b",
        "Reservation Request": r"\b(?:book|reserve|reservation|table|booking|reserve a spot|make a reservation|sign up|schedule)\b",
        "Check-In/Check-Out Request": r"\b(?:check-in|check out|early check-out|late check-in|early check|late checkout|arrival|departure)\b",
        "Negation": r"\b(?:no|not|don't|do not|never|can't|cannot|won't|will not)\b"
    }

    # Check for negations
    negation_found = re.search(intent_patterns["Negation"], text)
    
    # Iterate through patterns to find a match
    for intent, pattern in intent_patterns.items():
        if intent != "Negation" and re.search(pattern, text):
            # If negation is found, modify intent accordingly
            if negation_found:
                if intent in ["Room Service Order", "Amenities Request", "Reservation Request"]:
                    return f"Do not {intent.lower()}"
            return intent

    # If no patterns match, return Unknown Intent
    return "Unknown Intent"

# Example usage
test_queries = [
    "Can I order a pizza?",
    "What time is check-out?",
    "I am not happy with my room.",
    "Is breakfast included?",
    "I want to reserve a table for two.",
    "I don't want room service.",
    "Please bring extra towels."
]

for query in test_queries:
    intent = recognize_intent(query)
    print(f"Query: '{query}' -> Recognized Intent: '{intent}'")
