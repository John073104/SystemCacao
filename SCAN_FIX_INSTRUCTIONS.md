# Scan Diagnose Fixes

## Issues Found:
1. **Random results on each click** - Backend uses `random.choice()` causing different results for same image
2. **Cannot view full uploaded image** - Images are cropped with `object-cover`, no zoom/modal

## Fix 1: Make Scan Results Deterministic (Consistent)

### In `mainapp/views.py`, find the `simulate_analysis` function and replace it with:

```python
import hashlib

def simulate_analysis(scan_type, image_file=None):
    """Simulate ML analysis with deterministic results based on image hash"""
    classes, recommendations = (
        (DISEASE_CLASSES, DISEASE_RECOMMENDATIONS) if scan_type == 'disease' 
        else (PEST_CLASSES, PEST_RECOMMENDATIONS)
    )
    
    # Generate deterministic result based on image content
    if image_file:
        # Reset file pointer to beginning
        image_file.seek(0)
        # Create hash of image content
        image_hash = hashlib.md5(image_file.read()).hexdigest()
        # Reset file pointer again for later use
        image_file.seek(0)
        
        # Use hash to deterministically select class and confidence
        hash_int = int(image_hash[:8], 16)
        class_index = hash_int % len(classes)
        result_class = classes[class_index]
        
        # Generate deterministic confidence (75-98%)
        confidence = 0.75 + ((hash_int % 23) / 100.0)
    else:
        # Fallback to random if no image provided
        result_class = random.choice(classes)
        confidence = random.uniform(0.75, 0.98)
    
    return {
        'class': result_class,
        'confidence': confidence,
        'recommendations': recommendations.get(result_class, [])
    }
```

### Then update the `scan_image` function call to pass the image file:

Find this line:
```python
analysis_result = simulate_analysis(scan_type)
```

Replace with:
```python
analysis_result = simulate_analysis(scan_type, image_file)
```

## Fix 2: Add Image Preview Modal (Click to View Full Image)

This fix is already prepared in the updated template below.

## Complete Fixed Template

Save this as your new `scan_diagnose.html` - it includes:
- ✅ Deterministic results (same image = same result)
- ✅ Click to view full image in modal
- ✅ Better image preview with proper aspect ratio
- ✅ Image zoom functionality
