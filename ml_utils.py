import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os
from django.conf import settings

# Load models once when module is imported
DISEASE_MODEL_PATH = os.path.join(settings.BASE_DIR, 'models', 'cacao_disease_model.h5')
PEST_MODEL_PATH = os.path.join(settings.BASE_DIR, 'models', 'cacao_pest_model.h5')

try:
    disease_model = tf.keras.models.load_model(DISEASE_MODEL_PATH)
    pest_model = tf.keras.models.load_model(PEST_MODEL_PATH)
except Exception as e:
    print(f"Error loading models: {e}")
    disease_model = None
    pest_model = None

# Disease and pest class mappings
DISEASE_CLASSES = [
    'black_pod', 'witches_broom', 'frosty_pod', 'monilia', 'vascular_streak'
]

PEST_CLASSES = [
    'cocoa_pod_borer', 'mirids', 'thrips', 'mealybugs', 'aphids'
]

DISEASE_RECOMMENDATIONS = {
    'black_pod': 'Remove infected pods immediately. Improve drainage and air circulation. Apply copper-based fungicides.',
    'witches_broom': 'Prune infected branches 30cm below symptoms. Apply fungicide treatments during wet season.',
    'frosty_pod': 'Remove infected pods weekly. Apply protective fungicides before rainy season.',
    'monilia': 'Harvest pods frequently. Remove infected pods. Improve ventilation in plantation.',
    'vascular_streak': 'Remove infected trees. Plant resistant varieties. Improve soil drainage.'
}

PEST_RECOMMENDATIONS = {
    'cocoa_pod_borer': 'Regular pod harvesting. Remove infected pods. Use pheromone traps.',
    'mirids': 'Maintain shade trees. Use biological control agents. Apply targeted insecticides.',
    'thrips': 'Remove weeds around trees. Use blue sticky traps. Apply neem-based treatments.',
    'mealybugs': 'Prune infected parts. Use biological control with natural enemies. Apply systemic insecticides.',
    'aphids': 'Encourage natural predators. Use reflective mulches. Apply insecticidal soap.'
}

def preprocess_image(image_file):
    """Preprocess image for model prediction"""
    try:
        # Read image
        image = Image.open(image_file)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to model input size (assuming 224x224)
        image = image.resize((224, 224))
        
        # Convert to numpy array and normalize
        image_array = np.array(image) / 255.0
        
        # Add batch dimension
        image_array = np.expand_dims(image_array, axis=0)
        
        return image_array
    
    except Exception as e:
        raise Exception(f"Error preprocessing image: {str(e)}")

def predict_image(image_file):
    """Predict if image contains disease or pest and classify the type"""
    if disease_model is None or pest_model is None:
        raise Exception("ML models not loaded properly")
    
    try:
        # Preprocess image
        processed_image = preprocess_image(image_file)
        
        # Get predictions from both models
        disease_pred = disease_model.predict(processed_image)
        pest_pred = pest_model.predict(processed_image)
        
        # Get confidence scores
        disease_confidence = np.max(disease_pred)
        pest_confidence = np.max(pest_pred)
        
        # Determine which type based on higher confidence
        if disease_confidence > pest_confidence:
            scan_type = 'disease'
            class_idx = np.argmax(disease_pred)
            detected_class = DISEASE_CLASSES[class_idx]
            confidence = float(disease_confidence)
            recommendation = DISEASE_RECOMMENDATIONS.get(detected_class, 'Consult with agricultural expert.')
            
            result = {
                'type': scan_type,
                'disease_type': detected_class,
                'pest_type': None,
                'confidence': confidence,
                'recommendation': recommendation,
                'class_name': detected_class.replace('_', ' ').title()
            }
        else:
            scan_type = 'pest'
            class_idx = np.argmax(pest_pred)
            detected_class = PEST_CLASSES[class_idx]
            confidence = float(pest_confidence)
            recommendation = PEST_RECOMMENDATIONS.get(detected_class, 'Consult with agricultural expert.')
            
            result = {
                'type': scan_type,
                'disease_type': None,
                'pest_type': detected_class,
                'confidence': confidence,
                'recommendation': recommendation,
                'class_name': detected_class.replace('_', ' ').title()
            }
        
        return result
        
    except Exception as e:
        raise Exception(f"Error during prediction: {str(e)}")
