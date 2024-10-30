import os
import datetime
import json

LOG_FILE = os.path.join("logs", "interaction_logs.json")

def log_interaction(transcription, intent, sentiment, response, user_id='default_user'):
    # Ensure log folder exists
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    # Create a log entry
    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": user_id,
        "transcription": transcription,
        "intent": intent,
        "sentiment": sentiment,
        "response": response
    }
    
    try:
        # Append log entry to the log file
        with open(LOG_FILE, "a") as log_file:
            log_file.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"Error logging interaction: {e}")
