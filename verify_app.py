import requests
import json
import time

def test_prediction(message):
    print(f"\nTesting: {message[:50]}...")
    for _ in range(5):
        try:
            response = requests.post('http://localhost:5000/api/predict', json={'message': message}, timeout=10)
            if response.status_code == 200:
                res = response.json()
                print(f"Prediction: {res['prediction']}")
                print(f"Confidence: {res['confidence']}%")
                print(f"Language: {res['language']}")
                print(f"Phishing Links: {len(res['suspicious_links'])}")
                return res
            else:
                print(f"Error: {response.status_code}")
                return None
        except requests.exceptions.ConnectionError:
            print("Server not ready, retrying in 2s...")
            time.sleep(2)
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return None
    return None

if __name__ == "__main__":
    # Test cases
    test_prediction("Congratulations! You won a $1,000 gift card. Claim now at http://win-prize.xyz")
    test_prediction("अरे भाई, क्या हो रहा है? कल मिलें?")
    test_prediction("आपके बैंक खाते में संदिग्ध गतिविधि देखी गई है. कृपया यहाँ सत्यापित करें: http://bit.ly/bank-verify")
    test_prediction("I am coming over for dinner tonight. See you soon!")
