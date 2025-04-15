import joblib
import tensorflow as tf
from keras.models import load_model
import numpy as np
from PIL import Image
import io
import re


# Load ML Models
try:
    cnn_model = load_model("Model/cnn_skin_model.h5")
    mlp_model = joblib.load("Model/mlp_model.pkl")
    tfidf_vectorizer = joblib.load("Model/tfidf_vectorizer.pkl")
    mlb_encoder = joblib.load("Model/mlb_encoder.pkl")
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

        # Map index to label (customize as per your classes)
        labels = ["Dry", "Normal", "Oily", "Combination", "Sensitive"]
        return labels[predicted_label]
    except Exception as e:
        raise RuntimeError(f"Error predicting skin type: {str(e)}")


# Predict skin issues from text
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

def predict_skin_issues(description: str):
    try:
        if not description:
            return []

        # Clean text: remove non-letters and stop words
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

def generate_routine(skin_type: str, issues: list):
    routines = []

    # Skin-type specific routine
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

    # Add based on skin concerns
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
        # Add more as needed...
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
