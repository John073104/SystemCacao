import numpy as np
from PIL import Image
import io
from .models import DiseaseInfo, PestInfo

# mainapp/utils.py
import os
import tensorflow as tf
from django.conf import settings

def load_models():
    try:
        disease_model_path = os.path.join(settings.BASE_DIR, 'models', 'cacao_disease_model.h5')
        pest_model_path = os.path.join(settings.BASE_DIR, 'models', 'cacao_pest_model.h5')

        disease_model = tf.keras.models.load_model(disease_model_path)
        pest_model = tf.keras.models.load_model(pest_model_path)

        return disease_model, pest_model
    except Exception as e:
        print(f"Error loading models: {e}")
        return None, None

def preprocess_image(image_file):
    """Preprocess image for model prediction"""
    try:
        # Open and convert image
        image = Image.open(image_file)
        image = image.convert('RGB')
        
        # Resize to model input size (adjust based on your model)
        image = image.resize((224, 224))
        
        # Convert to numpy array and normalize
        image_array = np.array(image)
        image_array = image_array.astype('float32') / 255.0
        
        # Add batch dimension
        image_array = np.expand_dims(image_array, axis=0)
        
        return image_array
    except Exception as e:
        raise Exception(f"Error preprocessing image: {str(e)}")

def get_recommendations(prediction, scan_type):
    """Get recommendations based on prediction"""
    try:
        if scan_type == 'disease':
            try:
                disease_info = DiseaseInfo.objects.get(name=prediction)
                return f"Treatment: {disease_info.treatment}\n\nPrevention: {disease_info.prevention}"
            except DiseaseInfo.DoesNotExist:
                pass
        else:
            try:
                pest_info = PestInfo.objects.get(name=prediction)
                return f"Control Methods: {pest_info.control_methods}\n\nPrevention: {pest_info.prevention}"
            except PestInfo.DoesNotExist:
                pass
        
        # Default recommendations
        if prediction.lower() == 'healthy':
            return "Your cacao plant appears healthy! Continue with regular care and monitoring."
        
        return get_default_recommendations(prediction, scan_type)
    
    except Exception as e:
        return "Please consult with an agricultural expert for proper treatment."

def get_default_recommendations(prediction, scan_type):
    """Get default recommendations when database info is not available"""
    
    disease_recommendations = {
        'Black Pod Disease': """
        Treatment:
        - Remove and destroy infected pods immediately
        - Apply copper-based fungicides
        - Improve drainage and air circulation
        
        Prevention:
        - Regular pruning for better air circulation
        - Avoid overhead irrigation
        - Remove fallen pods and debris
        """,
        
        'Frosty Pod Rot': """
        Treatment:
        - Remove infected pods weekly
        - Apply protective fungicides during wet season
        - Improve farm sanitation
        
        Prevention:
        - Plant resistant varieties
        - Maintain proper spacing between trees
        - Regular monitoring and early detection
        """,
        
        'Witches Broom': """
        Treatment:
        - Prune infected branches 30cm below symptoms
        - Apply copper-based fungicides
        - Burn or bury infected material
        
        Prevention:
        - Use resistant varieties
        - Regular pruning and sanitation
        - Control humidity levels
        """,
        
        'Monilia Pod Rot': """
        Treatment:
        - Remove infected pods immediately
        - Apply fungicides preventively
        - Improve air circulation
        
        Prevention:
        - Harvest pods when mature
        - Regular farm sanitation
        - Avoid wounding pods during harvest
        """
    }
    
    pest_recommendations = {
        'Cocoa Pod Borer': """
        Control Methods:
        - Regular harvesting of ripe pods
        - Remove and destroy infested pods
        - Use pheromone traps
        - Apply appropriate insecticides
        
        Prevention:
        - Maintain farm cleanliness
        - Regular monitoring
        - Biological control agents
        """,
        
        'Thrips': """
        Control Methods:
        - Use blue sticky traps
        - Apply neem oil or insecticidal soap
        - Encourage beneficial insects
        
        Prevention:
        - Maintain proper humidity
        - Regular inspection of plants
        - Remove weeds that harbor thrips
        """,
        
        'Aphids': """
        Control Methods:
        - Spray with water to dislodge aphids
        - Apply neem oil or insecticidal soap
        - Introduce ladybugs or lacewings
        
        Prevention:
        - Avoid over-fertilizing with nitrogen
        - Encourage beneficial insects
        - Regular monitoring
        """,
        
        'Mealybugs': """
        Control Methods:
        - Remove with alcohol-soaked cotton swabs
        - Apply neem oil or insecticidal soap
        - Use systemic insecticides if severe
        
        Prevention:
        - Quarantine new plants
        - Regular inspection
        - Maintain proper plant spacing
        """
    }
    
    if scan_type == 'disease':
        return disease_recommendations.get(prediction, "Consult with an agricultural expert for proper disease management.")
    else:
        return pest_recommendations.get(prediction, "Consult with an agricultural expert for proper pest control.")

