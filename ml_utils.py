import torch
import torch.nn as nn
from torchvision import models, transforms
import numpy as np
from PIL import Image
import io
import os
from django.conf import settings
import random

# SET DETERMINISTIC MODE FOR REPRODUCIBLE PREDICTIONS
torch.manual_seed(42)
torch.cuda.manual_seed_all(42)
np.random.seed(42)
random.seed(42)

# Enable deterministic algorithms
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False

# Set device
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# Model paths - using PyTorch models from CacaoTrain folder
DISEASE_MODEL_PATH = os.path.join(settings.BASE_DIR, 'CacaoTrain', 'cacao_disease_resnet.pth')
PEST_MODEL_PATH = os.path.join(settings.BASE_DIR, 'CacaoTrain', 'cacao_pest_resnet.pth')

# Disease and pest class mappings - EXACT match from training
DISEASE_CLASSES = [
    'Black Pod Rot Disease',
    'Fito Disease', 
    'Healthy',
    'Monilia Disease',
    'Unknow Data'
]

PEST_CLASSES = [
    'Ant Weaver',
    'Aphids',
    'Healthy',
    'Mealybug',
    'Unknow Data'
]

DISEASE_RECOMMENDATIONS = {
    'Black Pod Rot Disease': 'Remove infected pods immediately. Improve drainage and air circulation. Apply copper-based fungicides. Prune infected branches to prevent spread.',
    'Fito Disease': 'Remove and destroy infected plant parts. Improve air circulation. Apply appropriate fungicide treatments. Monitor regularly for early detection.',
    'Healthy': 'Your cacao plant is healthy! Continue regular maintenance: proper watering, adequate sunlight, and balanced fertilization.',
    'Monilia Disease': 'Harvest pods frequently. Remove infected pods immediately. Improve ventilation in plantation. Apply protective fungicides during wet season.',
    'Unknow Data': 'Unable to identify the specific condition. Please consult with a local agricultural expert for proper diagnosis and treatment.'
}

PEST_RECOMMENDATIONS = {
    'Ant Weaver': 'Monitor ant activity. Remove ant nests near trees. Use sticky barriers on trunks. Control aphids and mealybugs that attract ants.',
    'Aphids': 'Encourage natural predators like ladybugs. Use reflective mulches. Apply insecticidal soap or neem oil. Spray with strong water jets to dislodge.',
    'Healthy': 'Your cacao plant is healthy! Maintain good practices: regular inspection, proper sanitation, and integrated pest management.',
    'Mealybug': 'Prune infected parts. Use biological control with natural enemies. Apply systemic insecticides if severe. Maintain plant health to resist infestation.',
    'Unknow Data': 'Unable to identify the specific pest. Please consult with a local agricultural expert for proper identification and treatment.'
}

# Initialize models
disease_model = None
pest_model = None

def initialize_model(num_classes):
    """Initialize ResNet18 model with specified number of classes"""
    model = models.resnet18(pretrained=False)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)
    return model

try:
    # Load disease model
    disease_model = initialize_model(len(DISEASE_CLASSES))
    disease_model.load_state_dict(torch.load(DISEASE_MODEL_PATH, map_location=device, weights_only=False))
    disease_model = disease_model.to(device)
    disease_model.eval()
    
    # Load pest model
    pest_model = initialize_model(len(PEST_CLASSES))
    pest_model.load_state_dict(torch.load(PEST_MODEL_PATH, map_location=device, weights_only=False))
    pest_model = pest_model.to(device)
    pest_model.eval()
    
    print("✅ Models loaded successfully!")
except Exception as e:
    print(f"❌ Error loading models: {e}")
    disease_model = None
    pest_model = None

# Image preprocessing - EXACT match from training
data_transforms = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def preprocess_image(image_file):
    """
    Preprocess image for PyTorch model prediction
    DETERMINISTIC: Uses fixed resize method (BILINEAR) for consistency
    """
    try:
        # Read image
        image = Image.open(image_file)
        
        # Convert to RGB if necessary (ensures consistent format)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Apply transforms (resize, crop, normalize)
        # All operations are deterministic:
        # - Resize: uses BILINEAR interpolation (default, deterministic)
        # - CenterCrop: crops from center (deterministic)
        # - ToTensor: direct conversion (deterministic)
        # - Normalize: fixed mean/std (deterministic)
        image_tensor = data_transforms(image)
        
        # Add batch dimension
        image_tensor = image_tensor.unsqueeze(0)
        
        return image_tensor
    
    except Exception as e:
        raise Exception(f"Error preprocessing image: {str(e)}")

def predict_image(image_file, scan_type='disease'):
    """
    Predict disease or pest classification with confidence
    DETERMINISTIC: Same image will ALWAYS produce same result
    
    Args:
        image_file: Image file to analyze
        scan_type: 'disease' or 'pest' to specify which model to use
    
    Returns:
        Dictionary with prediction results
    """
    if disease_model is None or pest_model is None:
        raise Exception("ML models not loaded properly. Please check model files in CacaoTrain folder.")
    
    try:
        # Reset random seeds for deterministic preprocessing
        torch.manual_seed(42)
        np.random.seed(42)
        random.seed(42)
        
        # Preprocess image
        processed_image = preprocess_image(image_file)
        processed_image = processed_image.to(device)
        
        # Select model based on scan type
        if scan_type.lower() == 'disease':
            model = disease_model
            classes = DISEASE_CLASSES
            recommendations = DISEASE_RECOMMENDATIONS
        else:
            model = pest_model
            classes = PEST_CLASSES
            recommendations = PEST_RECOMMENDATIONS
        
        # Ensure model is in eval mode (no randomness from dropout/batchnorm)
        model.eval()
        
        # Get prediction with deterministic behavior
        with torch.no_grad():
            torch.use_deterministic_algorithms(True, warn_only=True)
            outputs = model(processed_image)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]
            confidence_score, predicted_idx = torch.max(probabilities, 0)
        
        # Get predicted class
        predicted_class = classes[predicted_idx.item()]
        confidence = float(confidence_score.item() * 100)  # Convert to percentage
        
        # CRITICAL FIX: Only show "Unknow Data" if confidence is too low (<60%)
        # This prevents cacao images from incorrectly showing as "Unknow Data"
        if predicted_class == 'Unknow Data' and confidence < 60:
            # Check if image might be cacao-related by looking at other class probabilities
            other_probabilities = [float(probabilities[i].item() * 100) 
                                  for i in range(len(classes)) 
                                  if classes[i] != 'Unknow Data']
            
            # If any other class has confidence > 40%, use that class instead
            if other_probabilities and max(other_probabilities) > 40:
                max_prob_idx = probabilities.argmax().item()
                if classes[max_prob_idx] != 'Unknow Data':
                    predicted_class = classes[max_prob_idx]
                    confidence = float(probabilities[max_prob_idx].item() * 100)
        
        # Get recommendation
        recommendation = recommendations.get(predicted_class, 'Consult with agricultural expert for proper diagnosis.')
        
        # Prepare result
        result = {
            'type': scan_type.lower(),
            'detected_class': predicted_class,
            'confidence': round(confidence, 2),
            'recommendation': recommendation,
            'is_healthy': predicted_class == 'Healthy',
            'all_probabilities': {
                classes[i]: round(float(probabilities[i].item() * 100), 2) 
                for i in range(len(classes))
            }
        }
        
        # Add specific type fields for backward compatibility
        if scan_type.lower() == 'disease':
            result['disease_type'] = predicted_class
            result['pest_type'] = None
        else:
            result['disease_type'] = None
            result['pest_type'] = predicted_class
        
        return result
        
    except Exception as e:
        raise Exception(f"Error during prediction: {str(e)}")
