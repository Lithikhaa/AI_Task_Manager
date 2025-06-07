import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
import re


df = pd.read_csv('unique_tasks_dataset.csv')
print(f"Dataset shape: {df.shape}")
print(f"Categories: {df['label'].unique()}")
print(f"Label distribution:\n{df['label'].value_counts()}")

# Text preprocessing function
def preprocess_text(text):
    
    text = text.lower()
   
    text = re.sub(r'[^a-zA-Z\s]', '', text)
  
    text = ' '.join(text.split())
    return text


df['text_clean'] = df['text'].apply(preprocess_text)
print("Text preprocessing completed")

X = df['text_clean']
y = df['label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"Training samples: {len(X_train)}")
print(f"Testing samples: {len(X_test)}")



tfidf = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1, 2))
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)

print(f"Feature matrix shape: {X_train_tfidf.shape}")


models = {
    'Naive Bayes': MultinomialNB(),
    'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
    'SVM': SVC(random_state=42),
    'Random Forest': RandomForestClassifier(random_state=42, n_estimators=100)
}

results = {}

for name, model in models.items():
    print(f"\nTraining {name}...")
    model.fit(X_train_tfidf, y_train)

    # Predictions
    y_pred = model.predict(X_test_tfidf)

    # Accuracy
    accuracy = accuracy_score(y_test, y_pred)
    results[name] = accuracy

    print(f"{name} Accuracy: {accuracy:.4f}")

# Find best model
best_model_name = max(results, key=results.get)
best_model = models[best_model_name]
print(f"\n=== BEST MODEL: {best_model_name} (Accuracy: {results[best_model_name]:.4f}) ===")

y_pred_best = best_model.predict(X_test_tfidf)
print("\nClassification Report:")
print(classification_report(y_test, y_pred_best))

with open('task_categorizer_model.pkl', 'wb') as f:
    pickle.dump(best_model, f)

with open('tfidf_vectorizer.pkl', 'wb') as f:
    pickle.dump(tfidf, f)

print("Model and vectorizer saved successfully!")


def categorize_task(task_text):

    with open('task_categorizer_model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('tfidf_vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)

    # Preprocess the input
    clean_text = preprocess_text(task_text)

    # Transform to features
    text_tfidf = vectorizer.transform([clean_text])

    # Predict
    prediction = model.predict(text_tfidf)[0]
    probability = model.predict_proba(text_tfidf)[0]

    # Get confidence score
    confidence = max(probability)

    return prediction, confidence


test_task = "conducting a interview on 10pm"
category, confidence = categorize_task(test_task)

print(f"Input task: '{test_task}'")
print(f"Predicted category: {category}")
print(f"Confidence: {confidence:.4f}")


test_cases = [
    "conducting a interview on 10pm",
    "buy groceries from the store",
    "doctor appointment at 2pm",
    "finish work presentation by deadline",
    "book flight tickets for vacation",
    "clean the house this weekend",
    "study for final exam",
    "pay monthly bills online",
    "organize office files",
    "meet friends for dinner"
]

for i, task in enumerate(test_cases, 1):
    category, confidence = categorize_task(task)
    print(f"{i}. '{task}' → {category} (confidence: {confidence:.3f})")


print("Files saved:")
print("- task_categorizer_model.pkl")
print("- tfidf_vectorizer.pkl")
print("\nUse the categorize_task() function to classify new tasks!")


#trying 
import pickle
import re

def predict_category(task_text):
   
    with open('task_categorizer_model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('tfidf_vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)

  
    clean_text = task_text.lower()
    clean_text = re.sub(r'[^a-zA-Z\s]', '', clean_text)


    features = vectorizer.transform([clean_text])
    category = model.predict(features)[0]

    return category


task = "medical checkup"
result = predict_category(task)
print(result)