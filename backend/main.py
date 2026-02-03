from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import os

# Download stopwords if not already present
nltk.download('stopwords')

# Load model and vectorizer (update paths as needed)
MODEL_PATH = 'spam_model.joblib'
VECTORIZER_PATH = 'tfidf_vectorizer.joblib'

# Load trained model and vectorizer
model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)
stop_words = set(stopwords.words('english'))

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmailRequest(BaseModel):
    message: str

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)

@app.post("/predict")
async def predict_email(req: EmailRequest):
    clean = preprocess_text(req.message)
    vect = vectorizer.transform([clean])
    pred = model.predict(vect)[0]
    label = 'Spam' if pred == 1 else 'Ham'
    return {"prediction": label}

@app.get("/")
def root():
    return {"message": "Spam Detection API is running."}
