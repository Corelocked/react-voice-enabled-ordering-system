import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import nltk
from nltk.corpus import stopwords
import string
import joblib
from tqdm import tqdm

# Initialize tqdm for pandas
tqdm.pandas()

# Download NLTK stopwords if not already done
nltk.download('stopwords')

# Load the datasets
chunk_size = 10000  # Number of rows to read at a time
print("Loading reviews dataset in chunks...")
review_chunks = pd.read_json(
    r'C:\Users\Cedric Palapuz\Desktop\New folder\Yelp dataset\review.json', 
    lines=True, 
    chunksize=chunk_size
)
review_df = pd.concat(tqdm(review_chunks, desc="Processing review chunks"))  # Combine chunks into a single DataFrame

print("Loading business dataset...")
business_df = pd.read_json(r'C:\Users\Cedric Palapuz\Desktop\New folder\Yelp dataset\business.json', lines=True)

# Filter for restaurant-related businesses
print("Filtering for restaurants...")
restaurants = business_df[business_df['categories'].str.contains('Restaurant', na=False)]
restaurant_ids = restaurants['business_id'].unique()

# Get reviews for those restaurants
print("Filtering reviews for restaurants...")
restaurant_reviews = review_df[review_df['business_id'].isin(restaurant_ids)]

# Handle empty reviews
restaurant_reviews = restaurant_reviews[restaurant_reviews['text'].notnull() & (restaurant_reviews['text'].str.strip() != '')]

# Display the first few rows of reviews
print("Sample of restaurant reviews loaded:")
print(restaurant_reviews.head())

# Set up stopwords as a set for faster lookup
stop_words = set(stopwords.words('english'))

# Define a function to preprocess the review text
def preprocess_text(text):
    text = text.lower()  # Convert to lowercase
    text = text.translate(str.maketrans("", "", string.punctuation))  # Remove punctuation
    tokens = text.split()  # Split into words
    tokens = [word for word in tokens if word not in stop_words]  # Remove stopwords
    return ' '.join(tokens)

# Apply preprocessing to the review text with tqdm progress tracking
print("Preprocessing review text...")
restaurant_reviews['cleaned_text'] = restaurant_reviews['text'].progress_apply(preprocess_text)

# Display the first few rows of cleaned reviews
print("Sample of cleaned reviews:")
print(restaurant_reviews[['text', 'cleaned_text']].head())

# Define intent assignment function with keywords
def assign_intent(text):
    intent_keywords = {
        'Order Food': ['order', 'bring', 'get'],
        'Request Service': ['request', 'need', 'more'],
        'Give Feedback': ['not happy', 'complaint', 'issue'],
        'Make a Reservation': ['book', 'reserve', 'reservation']
    }
    for intent, keywords in intent_keywords.items():
        if any(keyword in text for keyword in keywords):
            return intent
    return 'Other'

# Apply the intent assignment with tqdm for progress tracking
print("Assigning intents to reviews...")
restaurant_reviews['intent'] = restaurant_reviews['cleaned_text'].progress_apply(assign_intent)

# Extract features and labels
X = restaurant_reviews['cleaned_text']
y = restaurant_reviews['intent']

# Vectorize text features with progress feedback
print("Vectorizing text...")
vectorizer = CountVectorizer()
X_vectorized = vectorizer.fit_transform(X)

# Remove the conversion to a dense DataFrame to avoid memory issues
# feature_df = pd.DataFrame(X_vectorized.toarray(), columns=vectorizer.get_feature_names_out())
# Instead, print the shape to confirm dimensions
print("Vectorized features shape:", X_vectorized.shape)

# Split the data into training and testing sets
print("Splitting data into train and test sets...")
X_train, X_test, y_train, y_test = train_test_split(X_vectorized, y, test_size=0.2, random_state=42)

# Train a logistic regression model with verbose progress
print("Training model...")
model = LogisticRegression(max_iter=200, verbose=1)
model.fit(X_train, y_train)


# Predict on the test set
print("Predicting on test set...")
y_pred = model.predict(X_test)

# Print the classification report
print("Classification Report:")
print(classification_report(y_test, y_pred))

# Save the model and vectorizer to disk
joblib.dump(model, 'logistic_regression_model.joblib')
joblib.dump(vectorizer, 'count_vectorizer.joblib')

print("Model and vectorizer saved to disk.")
