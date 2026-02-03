"""
Training script to train spam detection model with dataset balancing
Run this once to generate the trained model
"""
import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from sklearn.utils import resample
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import joblib
import os

# Download stopwords
nltk.download('stopwords', quiet=True)

print("=" * 60)
print("SPAM DETECTION MODEL TRAINING")
print("=" * 60)

# Load dataset
print("\n[1/6] Loading dataset...")
url = 'https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv'
df = pd.read_csv(url, sep='\t', header=None, names=['label', 'message'])
print(f"Dataset loaded: {len(df)} messages")

# Show original distribution
print(f"\nOriginal class distribution:")
print(df['label'].value_counts())

# ============ BALANCE THE DATASET ============
print("\n[2/6] Balancing dataset (handling bias)...")
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)

# Apply preprocessing
df['clean_message'] = df['message'].apply(preprocess_text)

# Separate ham and spam
df_ham = df[df['label'] == 'ham']
df_spam = df[df['label'] == 'spam']

# Upsample spam to match ham count (handles bias)
df_spam_upsampled = resample(df_spam, 
                             replace=True, 
                             n_samples=len(df_ham), 
                             random_state=42)

# Combine and shuffle
df_balanced = pd.concat([df_ham, df_spam_upsampled])
df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"Balanced class distribution:")
print(df_balanced['label'].value_counts())

# ============ FEATURE EXTRACTION ============
print("\n[3/6] Extracting TF-IDF features...")
vectorizer = TfidfVectorizer(max_features=3000, min_df=2, max_df=0.8)
X = vectorizer.fit_transform(df_balanced['clean_message'])
y = df_balanced['label'].map({'ham': 0, 'spam': 1})
print(f"Features extracted: {X.shape}")

# ============ TRAIN-TEST SPLIT ============
print("\n[4/6] Splitting data (80-20)...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Training samples: {X_train.shape[0]}")
print(f"Testing samples: {X_test.shape[0]}")

# ============ MODEL TRAINING ============
print("\n[5/6] Training Naive Bayes model...")
model = MultinomialNB()
model.fit(X_train, y_train)

# ============ MODEL EVALUATION ============
print("\n[6/6] Evaluating model...")
y_pred = model.predict(X_test)

acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"\n✓ Accuracy:  {acc:.4f}")
print(f"✓ Precision: {prec:.4f}")
print(f"✓ Recall:    {rec:.4f}")
print(f"✓ F1-Score:  {f1:.4f}")

print("\nDetailed Classification Report:")
print(classification_report(y_test, y_pred, target_names=['Ham', 'Spam']))

# ============ SAVE MODEL ============
print("\n[SAVING] Exporting model and vectorizer...")
model_dir = 'models'
os.makedirs(model_dir, exist_ok=True)

joblib.dump(model, f'{model_dir}/spam_model.pkl')
joblib.dump(vectorizer, f'{model_dir}/tfidf_vectorizer.pkl')

print(f"✓ Model saved to: {model_dir}/spam_model.pkl")
print(f"✓ Vectorizer saved to: {model_dir}/tfidf_vectorizer.pkl")

print("\n" + "=" * 60)
print("✓ TRAINING COMPLETE - Ready to use in Flask app!")
print("=" * 60)
