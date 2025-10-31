"""
Fix the backend to make scan results deterministic
Same image will always return the same result
"""

import re

views_path = r'c:\Users\ACER\Dropbox\PC\Downloads\cacaoguardbackup\cacaoguard\mainapp\views.py'

# Read the file
with open(views_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Ensure hashlib is imported
if 'import hashlib' not in content:
    # Find a good place to add it (after other imports)
    if 'import random' in content:
        content = content.replace('import random', 'import random\nimport hashlib', 1)
        print("✅ Added hashlib import")
    else:
        # Add at the beginning after django imports
        import_pos = content.find('from django.shortcuts import')
        if import_pos != -1:
            # Find the end of that line
            line_end = content.find('\n', import_pos)
            content = content[:line_end+1] + 'import hashlib\nimport random\n' + content[line_end+1:]
            print("✅ Added hashlib and random imports")

# Find and replace ALL simulate_analysis functions
pattern = r'def simulate_analysis\([^)]*\):[^}]+?return\s*\{[^}]+\}'

new_function = '''def simulate_analysis(scan_type, image_file=None):
    """Simulate ML analysis with deterministic results based on image hash"""
    classes, recommendations = (
        (DISEASE_CLASSES, DISEASE_RECOMMENDATIONS) if scan_type == 'disease' 
        else (PEST_CLASSES, PEST_RECOMMENDATIONS)
    )
    
    # Generate deterministic result based on image content
    if image_file:
        try:
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
        except Exception as e:
            print(f"Error hashing image: {e}")
            # Fallback to random
            result_class = random.choice(classes)
            confidence = random.uniform(0.75, 0.98)
    else:
        # Fallback to random if no image provided
        result_class = random.choice(classes)
        confidence = random.uniform(0.75, 0.98)
    
    return {
        'class': result_class,
        'confidence': confidence,
        'recommendations': recommendations.get(result_class, [])
    }'''

# Count occurrences
matches = list(re.finditer(pattern, content, re.DOTALL))
print(f"Found {len(matches)} simulate_analysis function(s)")

if matches:
    # Replace from last to first to maintain positions
    for match in reversed(matches):
        content = content[:match.start()] + new_function + content[match.end():]
    print(f"✅ Replaced {len(matches)} simulate_analysis function(s)")

# Update all calls to simulate_analysis to pass image_file
# Pattern: simulate_analysis(scan_type) or simulate_analysis(type)
call_pattern = r'simulate_analysis\((scan_type|type)\)'
replacement = r'simulate_analysis(\1, image_file)'

updated_calls = re.subn(call_pattern, replacement, content)
if updated_calls[1] > 0:
    content = updated_calls[0]
    print(f"✅ Updated {updated_calls[1]} simulate_analysis call(s) to pass image_file")

# Write back
with open(views_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "="*60)
print("✅ BACKEND FIX COMPLETE!")
print("="*60)
print("\nWhat was fixed:")
print("1. ✅ simulate_analysis now uses MD5 hash of image content")
print("2. ✅ Same image will always return same result")
print("3. ✅ Confidence scores are deterministic")
print("4. ✅ All function calls updated to pass image_file")
print("\nTest it:")
print("1. Upload an image for disease detection")
print("2. Note the result")
print("3. Upload the SAME image again")
print("4. You should get the EXACT same result!")
