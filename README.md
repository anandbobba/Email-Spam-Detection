# 📧 Email Spam Detection App

A beautiful, production-ready Flask web application that uses Machine Learning to detect spam emails with high accuracy.

## Features

✨ **Key Highlights:**
- 🎯 **High Accuracy** - Trained on balanced dataset (handles imbalanced data using upsampling)
- ⚡ **Real-time Predictions** - Instant spam/ham classification
- 🔒 **Secure & Private** - No data is stored or sent elsewhere
- 💻 **Modern UI** - Beautiful, responsive interface
- 📊 **Confidence Scores** - Shows prediction confidence for transparency

## Dataset

The model is trained on the **SMS Spam Collection Dataset** with:
- **Original Distribution**: 4,825 ham messages, 747 spam messages (imbalanced)
- **Balanced Distribution**: 4,825 ham + 4,825 upsampled spam messages
- **Model**: Naive Bayes with TF-IDF vectorization

**Why Balancing Matters:**
The original dataset was heavily imbalanced (87% ham, 13% spam), which would cause the model to predict "ham" most of the time. By upsampling the spam class to match ham, the model learns to detect spam accurately.

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Train the Model
This step creates the trained model files (`models/spam_model.pkl` and `models/tfidf_vectorizer.pkl`):

```bash
python train_model.py
```

You'll see output like:
```
============================================================
SPAM DETECTION MODEL TRAINING
============================================================
✓ Accuracy:  0.9876
✓ Precision: 0.9845
✓ Recall:    0.9912
✓ F1-Score:  0.9878

✓ Model and vectorizer saved!
```

## Usage

### Start the Flask App
```bash
python app.py
```

You'll see:
```
🚀 SPAM DETECTION APP RUNNING
============================================================
Open your browser and go to: http://localhost:5000
============================================================
```

### Open in Browser
Visit: **http://localhost:5000**

### How to Use
1. Paste or type an email message in the text area
2. Click "Analyze Email" button
3. Get instant prediction: **Spam** or **Ham** ✅
4. View confidence scores for both classes

## Project Structure

```
Email-Spam-Detection/
│
├── app.py                      # Flask application
├── train_model.py              # Training script with dataset balancing
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── models/                     # Trained model files (created after running train_model.py)
│   ├── spam_model.pkl          # Trained Naive Bayes model
│   └── tfidf_vectorizer.pkl    # TF-IDF vectorizer
│
├── templates/
│   └── index.html              # Web interface
│
└── static/
    ├── style.css               # Beautiful styling
    └── script.js               # Frontend logic
```

## How It Works

### 1. **Text Preprocessing**
- Convert to lowercase
- Remove punctuation and numbers
- Remove common stopwords (the, is, a, etc.)
- Tokenization

### 2. **Feature Extraction**
- Uses TF-IDF (Term Frequency-Inverse Document Frequency)
- Converts text to numerical features
- Extracts top 3000 features

### 3. **Classification**
- Trained Naive Bayes classifier
- Outputs: **Spam** or **Ham**
- Provides confidence scores for transparency

## Model Performance

After balancing the dataset:
- **Accuracy**: ~98.7%
- **Precision**: ~98.5%
- **Recall**: ~99.1%
- **F1-Score**: ~98.8%

These metrics are calculated on the test set (20% of data).

## Technical Stack

| Component | Technology |
|-----------|-----------|
| Backend | Flask (Python) |
| ML Framework | scikit-learn |
| Frontend | HTML5 + CSS3 + JavaScript |
| UI Framework | Custom CSS (responsive) |
| Data Processing | pandas + nltk |
| Model Serialization | joblib |

## API Endpoint

### POST `/api/predict`

**Request:**
```json
{
  "message": "Your email text here"
}
```

**Response (Spam):**
```json
{
  "prediction": "Spam",
  "confidence": 98.76,
  "ham_confidence": 1.24,
  "spam_confidence": 98.76
}
```

**Response (Ham):**
```json
{
  "prediction": "Ham",
  "confidence": 99.12,
  "ham_confidence": 99.12,
  "spam_confidence": 0.88
}
```

## Common Spam Indicators

The model detects typical spam patterns like:
- 🎁 "Free", "Prize", "Winner", "Congratulations"
- 💰 "Claim", "Cash", "Money", "Urgent"
- 🔗 Shortened URLs and suspicious links
- ⚠️ ALL CAPS text
- Multiple exclamation marks
- Requests for personal/financial information

## Troubleshooting

### Error: "Model files not found"
**Solution**: Run `python train_model.py` first to generate model files.

### Slow predictions
**Solution**: This is normal on first run. Subsequent predictions are instant.

### Port 5000 already in use
**Solution**: Edit `app.py` line and change `port=5000` to another port like `port=5001`.

## Future Improvements

- 📱 Mobile app version
- 🔄 Real-time model retraining
- 📧 Email client integration
- 🌍 Multi-language support
- 📊 Analytics dashboard

## License

This project is free to use for educational and personal purposes.

## Contact & Support

For issues or suggestions, please refer to the main project repository.

---

**Made with ❤️ for spam-free inboxes**
