"""
Flask app for Email Spam Detection
"""
from flask import Flask, render_template, request, jsonify
import joblib
import re
import nltk
from nltk.corpus import stopwords
import os

# Download stopwords
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

app = Flask(__name__, template_folder='templates', static_folder='static')

# Load pre-trained model and vectorizer
MODEL_PATH = 'models/spam_model.pkl'
VECTORIZER_PATH = 'models/tfidf_vectorizer.pkl'

if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
    print("\n❌ ERROR: Model files not found!")
    print("Please run: python train_model.py")
    exit(1)

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)
stop_words = set(stopwords.words('english'))

print("✓ Model and vectorizer loaded successfully")

def preprocess_text(text):
    """Preprocess text for spam detection"""
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    return ' '.join(tokens)

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict():
    """API endpoint to predict spam/ham"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Please enter a message'}), 400
        
        # Preprocess
        clean = preprocess_text(message)
        
        # Vectorize
        vect = vectorizer.transform([clean])
        
        # Predict
        pred = model.predict(vect)[0]
        confidence = model.predict_proba(vect)[0]
        
        result = {
            'prediction': 'Spam' if pred == 1 else 'Ham',
            'confidence': float(max(confidence) * 100),
            'ham_confidence': float(confidence[0] * 100),
            'spam_confidence': float(confidence[1] * 100)
        }
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 SPAM DETECTION APP RUNNING")
    print("=" * 60)
    print("Open your browser and go to: http://localhost:5000")
    print("=" * 60 + "\n")
    app.run(debug=True, port=5000)
