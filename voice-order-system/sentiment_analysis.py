from transformers import pipeline

# Load sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis")

def analyze_sentiment(text):
    # Analyze the sentiment of the input text
    result = sentiment_analyzer(text)
    sentiment_label = result[0]['label']  # 'POSITIVE' or 'NEGATIVE'
    sentiment_score = result[0]['score']  # Confidence score

    # Determine overall sentiment based on label
    return sentiment_label, sentiment_score

# Example usage
if __name__ == "__main__":
    sample_text = "I love the service here, but the food was disappointing."
    sentiment, score = analyze_sentiment(sample_text)
    print(f"Sentiment: {sentiment}, Score: {score:.2f}")
