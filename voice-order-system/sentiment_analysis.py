from transformers import pipeline

# Load sentiment analysis pipeline with explicit model
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def analyze_sentiment(text):
    try:
        # Analyze the sentiment of the input text
        result = sentiment_analyzer(text)
        sentiment_label = result[0]['label']  # 'POSITIVE' or 'NEGATIVE'
        sentiment_score = result[0]['score']  # Confidence score

        return sentiment_label, sentiment_score
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return None, None

def generate_response_based_on_sentiment(text):
    sentiment, score = analyze_sentiment(text)
    
    if sentiment == "POSITIVE":
        response = f"Thank you for sharing that! We're so glad you had a great experience. Your feedback means a lot to us!"
    
    elif sentiment == "NEGATIVE":
        response = f"We're really sorry to hear that. We value your feedback and will work on improving. Can you please share more details about your experience?"
    
    else:
        response = "Thank you for your input! If you have any specific requests or concerns, feel free to let us know."
    
    return response