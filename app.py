"""
Professional Email Spam & Phishing Detection System
Multilingual | SVM Model | Real-Time Scoring | Threat Categorisation
"""
from flask import Flask, render_template, request, jsonify
import joblib
import re
import os
import nltk
from nltk.corpus import stopwords
from langdetect import detect, DetectorFactory
from urllib.parse import urlparse

# Reproducible language detection
DetectorFactory.seed = 42

# NLTK
nltk.download('stopwords', quiet=True)
STOP_WORDS = set(stopwords.words('english'))

app = Flask(__name__, template_folder='templates', static_folder='static')

# ─── MODEL LOADING ────────────────────────────────────────────────────────────

MODEL_PATH = 'models/spam_model.pkl'
VECTORIZER_PATH = 'models/tfidf_vectorizer.pkl'
ml_model = None
ml_vectorizer = None

if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
    try:
        ml_model = joblib.load(MODEL_PATH)
        ml_vectorizer = joblib.load(VECTORIZER_PATH)
        print("ML model loaded: spam_model.pkl")
    except Exception as e:
        print(f"Model load error: {e}")
else:
    print("No trained model found. Run train_model.py first.")

# ─── KNOWLEDGE BASE ───────────────────────────────────────────────────────────

# English threat categories with weighted keywords
THREAT_CATEGORIES = {
    'financial': {
        'label': 'Financial Exploitation',
        'weight': 30,
        'keywords': ['prize', 'winner', 'cash', 'money', 'reward', 'claim', 'bonus',
                     'lottery', 'jackpot', 'gift card', '£', '$', 'free', 'win',
                     'bank account', 'transfer', 'payment', 'refund']
    },
    'urgency': {
        'label': 'Urgency / Pressure',
        'weight': 25,
        'keywords': ['urgent', 'immediately', 'expire', 'expiry', 'limited time',
                     'act now', 'hurry', 'deadline', 'warning', 'attention', 'final notice',
                     'last chance', 'today only', 'don\'t miss']
    },
    'phishing': {
        'label': 'Phishing / Identity',
        'weight': 35,
        'keywords': ['verify', 'confirm', 'update', 'login', 'password', 'account',
                     'suspend', 'security', 'alert', 'click here', 'follow the link',
                     'provide your', 'personal details', 'otp', 'ssn', 'credentials']
    },
    'social': {
        'label': 'Social Engineering',
        'weight': 20,
        'keywords': ['congratulations', 'you have been selected', 'special offer',
                     'exclusive', 'guaranteed', 'risk-free', 'no cost', 'call now',
                     'customer service', 'representative', 'apply now']
    }
}

# Indic language keywords mapped to English categories
INDIC_SPAM_KEYWORDS = {
    'hi': {
        'financial': ['पैसा', 'इनाम', 'पुरस्कार', 'जीत', 'लॉटरी', 'मुफ्त', 'बधाई'],
        'urgency':   ['जल्दी', 'तुरंत', 'अभी', 'अंतिम', 'चेतावनी'],
        'phishing':  ['बैंक', 'खाता', 'सत्यापित', 'लॉगिन', 'पासवर्ड', 'ओटीपी'],
    },
    'bn': {
        'financial': ['টাকা', 'পুরস্কার', 'জয়', 'লটারি', 'বিনামূল্যে', 'অভিনন্দন'],
        'urgency':   ['দ্রুত', 'তাৎক্ষণিক', 'এখনই', 'সতর্কতা'],
        'phishing':  ['ব্যাংক', 'অ্যাকাউন্ট', 'যাচাই', 'পাসওয়ার্ড'],
    },
    'te': {
        'financial': ['డబ్బు', 'బహుమతి', 'గెలుపు', 'లాటరీ', 'ఉచితం', 'అభినందనలు'],
        'urgency':   ['తొందరగా', 'వెంటనే', 'హెచ్చరిక'],
        'phishing':  ['బ్యాంక్', 'ఖాతా', 'ధృవీకరించండి'],
    },
    'mr': {
        'financial': ['पैसा', 'बक्षीस', 'विजय', 'लॉटरी', 'मोफत', 'अभिनंदन'],
        'urgency':   ['त्वरीत', 'लगेच', 'इशारा'],
        'phishing':  ['बँक', 'खाते', 'सत्यापित', 'पासवर्ड'],
    },
    'ta': {
        'financial': ['பணம்', 'பரிசு', 'வெற்றி', 'லாட்டரி', 'இலவசம்', 'வாழ்த்துக்கள்'],
        'urgency':   ['விரைவாக', 'உடனடியாக', 'எச்சரிக்கை'],
        'phishing':  ['வங்கி', 'கணக்கு', 'சரிபார்க்கவும்'],
    }
}

SUSPICIOUS_TLDS = {'.xyz', '.top', '.loan', '.win', '.icu', '.club', '.link', '.click', '.ly', '.tk', '.ml'}

LANG_MAP = {
    'en': 'English', 'hi': 'Hindi', 'bn': 'Bengali', 'te': 'Telugu',
    'mr': 'Marathi', 'ta': 'Tamil', 'gu': 'Gujarati', 'kn': 'Kannada',
    'ml': 'Malayalam', 'pa': 'Punjabi', 'ur': 'Urdu'
}

# ─── CORE ANALYSIS ENGINE ─────────────────────────────────────────────────────

def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    return ' '.join([w for w in text.split() if w not in STOP_WORDS and len(w) > 1])

def detect_language(text):
    try:
        code = detect(text)
        return code, LANG_MAP.get(code, 'Global')
    except:
        return 'en', 'English'

def extract_links(text):
    return re.findall(r'https?://[^\s]+', text)

def analyze_links(links):
    suspicious = []
    for link in links:
        try:
            domain = urlparse(link).netloc.lower()
            if any(tld in domain for tld in SUSPICIOUS_TLDS) or len(domain.split('.')) > 3:
                suspicious.append(link)
        except:
            pass
    return suspicious

def analyze_threats(text, lang):
    """Returns categorised threat analysis with scores."""
    text_lower = text.lower()
    results = {}
    total_threat_score = 0

    # English threat categories
    for cat_key, cat_data in THREAT_CATEGORIES.items():
        hits = [kw for kw in cat_data['keywords'] if kw in text_lower]
        if hits:
            score = min(len(hits) * (cat_data['weight'] // 2), cat_data['weight'])
            results[cat_key] = {'label': cat_data['label'], 'hits': hits, 'score': score}
            total_threat_score += score

    # Indic keyword overlay
    if lang in INDIC_SPAM_KEYWORDS:
        for cat_key, kw_list in INDIC_SPAM_KEYWORDS[lang].items():
            hits = [kw for kw in kw_list if kw in text]
            if hits:
                bonus = min(len(hits) * 10, 20)
                total_threat_score += bonus
                if cat_key in results:
                    results[cat_key]['hits'] += hits
                    results[cat_key]['score'] += bonus
                else:
                    label = THREAT_CATEGORIES.get(cat_key, {}).get('label', cat_key.title())
                    results[cat_key] = {'label': label, 'hits': hits, 'score': bonus}

    return results, min(total_threat_score, 99)

def run_inference(message, lang):
    """Run the ML model if available, else rule-based scoring."""
    if ml_model and ml_vectorizer and lang == 'en':
        cleaned = preprocess(message)
        vec = ml_vectorizer.transform([cleaned])
        prob = ml_model.predict_proba(vec)[0][1] * 100
        return float(prob), 'ml'
    return None, 'rules'

# ─── API ENDPOINTS ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/quick-score', methods=['POST'])
def quick_score():
    """Lightweight endpoint for real-time typing analysis."""
    try:
        data = request.json
        message = (data.get('message') or '').strip()
        if not message or len(message) < 5:
            return jsonify({'score': 0}), 200

        lang_code, _ = detect_language(message)
        links = extract_links(message)
        susp = analyze_links(links)
        _, rule_score = analyze_threats(message, lang_code)

        ml_prob, source = run_inference(message, lang_code)

        if ml_prob is not None:
            base = ml_prob
        else:
            base = rule_score

        if susp:
            base = max(base, 82.0)

        return jsonify({'score': round(float(base), 1), 'source': source}), 200
    except Exception as e:
        return jsonify({'score': 0, 'error': str(e)}), 200  # Always return 200 for real-time

@app.route('/api/predict', methods=['POST'])
def predict():
    """Full analysis endpoint with categorised threat breakdown."""
    try:
        data = request.json
        message = (data.get('message') or '').strip()
        if not message:
            return jsonify({'error': 'No input provided'}), 400

        lang_code, lang_name = detect_language(message)
        links = extract_links(message)
        susp_links = analyze_links(links)
        threats, rule_score = analyze_threats(message, lang_code)

        ml_prob, source = run_inference(message, lang_code)

        if ml_prob is not None:
            confidence = ml_prob
        else:
            confidence = rule_score if rule_score > 15 else 5.0

        if susp_links:
            confidence = max(confidence, 82.0)

        prediction = 'Spam' if confidence >= 50 else 'Legitimate'

        # Build keyword list from all categories
        all_keywords = []
        for cat in threats.values():
            all_keywords.extend(cat.get('hits', []))

        return jsonify({
            'prediction': prediction,
            'confidence': round(float(confidence), 1),
            'language': lang_name,
            'source': source,
            'suspicious_links': susp_links,
            'threats': threats,
            'keywords': list(set(all_keywords))
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Spam Detection Server running on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
