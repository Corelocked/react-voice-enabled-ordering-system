import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

# Load dataset
data_path = 'inquiries.csv'  # Update path as needed
df = pd.read_csv(data_path)

# Print column names to verify
print("Columns in dataset:", df.columns)

# Update column names based on actual dataset structure
inquiry_column = 'Question'  # Use 'Question' instead of 'Query'
response_column = 'Response'  # This remains the same

# Check if columns exist
if inquiry_column not in df.columns or response_column not in df.columns:
    raise KeyError(f"Expected columns '{inquiry_column}' and '{response_column}' not found in the dataset.")

# Preprocess the data
df[inquiry_column] = df[inquiry_column].str.lower()

# Vectorize the queries
vectorizer = CountVectorizer(ngram_range=(1, 2), max_features=1000)
X = vectorizer.fit_transform(df[inquiry_column])
y = df[response_column]

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize the model
model = MultinomialNB()

# Train the model
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Evaluate model accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Model accuracy: {accuracy:.2f}")

# Print classification report
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save model and vectorizer if accuracy is acceptable
if accuracy > 0.7:
    os.makedirs('models', exist_ok=True)
    joblib.dump(model, 'models/inquiry_intent_model.joblib')
    joblib.dump(vectorizer, 'models/inquiry_vectorizer.joblib')
    print("Model and vectorizer saved successfully.")
else:
    print("Model accuracy is below the threshold. Consider improving the dataset or tuning the model.")
