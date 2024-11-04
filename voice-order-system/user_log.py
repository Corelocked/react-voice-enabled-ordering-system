import os
import datetime

LOG_FILE = os.path.join("logs", "interaction_logs.txt")
FEEDBACK_FILE = os.path.join("logs", "feedback_logs.txt")

def log_interaction(transcription, intent, sentiment, response):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    try:
        with open(LOG_FILE, "a") as log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"[{timestamp}] Transcription: '{transcription}' | Intent: {intent} | Sentiment: {sentiment} | Response: {response}\n")
    except Exception as e:
        print(f"Error logging interaction: {str(e)}")  # Optionally log to console or a dedicated error log

def log_feedback(feedback):
    os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)

    try:
        with open(FEEDBACK_FILE, "a") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] Feedback: '{feedback}'\n")
    except Exception as e:
        print(f"Error logging feedback: {str(e)}")  # Optionally log to console or a dedicated error log
