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

# Example usage
if __name__ == "__main__":
    sample_texts = [
        "I love the service here, but the food was disappointing.",
        "The ambiance was great and the food was delicious!",
        "I had a terrible experience."
    ]
    for text in sample_texts:
        sentiment, score = analyze_sentiment(text)
        print(f"Text: \"{text}\" | Sentiment: {sentiment}, Score: {score:.2f}")
