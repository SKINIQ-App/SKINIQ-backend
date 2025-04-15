import joblib
import tensorflow as tf
from keras.models import load_model
import numpy as np
from PIL import Image
import io
import re
import requests
import os
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

# URLs for the hosted model files on GitHub Releases
cnn_model_url = 'https://github.com/SKINIQ-App/SKINIQ-backend/releases/download/v1.0/cnn_skin_model.h5'
mlp_model_url = 'https://github.com/SKINIQ-App/SKINIQ-backend/releases/download/v1.0/mlp_model.pkl'
tfidf_vectorizer_url = 'https://github.com/SKINIQ-App/SKINIQ-backend/releases/download/v1.0/tfidf_vectorizer.pkl'
mlb_encoder_url = 'https://github.com/SKINIQ-App/SKINIQ-backend/releases/download/v1.0/mlb_encoder.pkl'

# Paths to save models locally
cnn_model_path = 'Model/cnn_skin_model.h5'
mlp_model_path = 'Model/mlp_model.pkl'
tfidf_vectorizer_path = 'Model/tfidf_vectorizer.pkl'
mlb_encoder_path = 'Model/mlb_encoder.pkl'

# Download the models if they don't exist locally
def download_model(url, path):
    if not os.path.exists(path):
        try:
            print(f"Downloading model from {url}...")
            headers = {"User-Agent": "python-requests/2.25.1"}
            response = requests.get(url, stream=True, headers=headers)
            response.raise_for_status()

            os.makedirs(os.path.dirname(path), exist_ok=True)

            with open(path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"Model downloaded successfully to {path}!")
        except requests.exceptions.HTTPError as e:
            print(f"[ERROR] Failed to download model: {e.response.status_code} - {e.response.reason}")
            print(f"[DEBUG] URL tried: {url}")
            raise RuntimeError(f"Error downloading model: {str(e)}")
        except Exception as e:
            print(f"[ERROR] Unknown error during model download: {str(e)}")
            raise RuntimeError(f"Error downloading model: {str(e)}")

# Download all required models and files
download_model(cnn_model_url, cnn_model_path)
download_model(mlp_model_url, mlp_model_path)
download_model(tfidf_vectorizer_url, tfidf_vectorizer_path)
download_model(mlb_encoder_url, mlb_encoder_path)

# Load ML Models
try:
    cnn_model = load_model(cnn_model_path)
    mlp_model = joblib.load(mlp_model_path)
    tfidf_vectorizer = joblib.load(tfidf_vectorizer_path)
    mlb_encoder = joblib.load(mlb_encoder_path)
except Exception as e:
    raise RuntimeError(f"Error loading models: {str(e)}")

__all__ = ["cnn_model", "mlp_model", "tfidf_vectorizer", "mlb_encoder"]

# Predict skin type from image
def predict_skin_type(image_file):
    try:
        image = Image.open(image_file).convert("RGB")
        image = image.resize((150, 150))  # match model input size
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)

        prediction = cnn_model.predict(image_array)
        predicted_label = np.argmax(prediction, axis=1)[0]

        labels = ["Dry", "Normal", "Oily", "Combination", "Sensitive"]
        return labels[predicted_label]
    except Exception as e:
        raise RuntimeError(f"Error predicting skin type: {str(e)}")

# Predict skin issues from text
def predict_skin_issues(description: str):
    try:
        if not description:
            return []

        text = re.sub(r"[^a-zA-Z\s]", "", description.lower())
        cleaned_text = " ".join([
            word for word in text.split()
            if word not in ENGLISH_STOP_WORDS
        ])

        if not cleaned_text.strip():
            return []

        X = tfidf_vectorizer.transform([cleaned_text])
        prediction = mlp_model.predict(X)
        predicted_labels = mlb_encoder.inverse_transform(prediction)

        return list(predicted_labels[0])
    except Exception as e:
        raise RuntimeError(f"Error predicting skin issues: {str(e)}")

# Generate skin routine
def generate_routine(skin_type: str, issues: list):
    routines = []

    if skin_type.lower() == "dry":
        routines.append("Use hydrating cleanser and thick moisturizer")
    elif skin_type.lower() == "oily":
        routines.append("Use oil-free cleanser and exfoliate regularly")
    elif skin_type.lower() == "sensitive":
        routines.append("Use fragrance-free, calming skincare")
    elif skin_type.lower() == "normal":
        routines.append("Maintain gentle routine with SPF")
    elif skin_type.lower() == "combinational":
        routines.append("Balance hydration and exfoliation in different zones")

    issue_routines = {
        "acne": "Use salicylic acid cleanser and niacinamide serum",
        "dark circle": "Use eye cream with caffeine and hydrate well",
        "hyperpigmentation": "Use vitamin C serum and sunscreen",
        "blackheads": "Use BHA exfoliants twice a week",
        "wrinkles": "Use retinol at night and SPF in day",
        "dull skin": "Use AHA exfoliant and hydrate with hyaluronic acid",
        "eczema": "Use thick emollient creams and avoid triggers",
        "redness": "Use calming products with aloe or chamomile",
        "dark spots": "Use niacinamide and brightening agents",
    }

    matched = False
    for issue in issues:
        for key in issue_routines:
            if key in issue.lower():
                routines.append(issue_routines[key])
                matched = True

    if not matched:
        routines.append("Use gentle skincare and consult a dermatologist")

    return routines


__all__ = ["cnn_model", "mlp_model", "tfidf_vectorizer", "mlb_encoder",
           "predict_skin_type", "predict_skin_issues", "generate_routine"]
