"""
Script to fix the simulate_analysis function in views.py
This makes scan results deterministic (same image = same result)
"""

import re

views_path = r'c:\Users\ACER\Dropbox\PC\Downloads\cacaoguardbackup\cacaoguard\mainapp\views.py'

# Read the file
with open(views_path, 'r', encoding='utf-8') as f:
    content = f.read()

# New deterministic simulate_analysis function
new_function = '''import hashlib

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
    }'''

# Pattern to find simulate_analysis functions
pattern = r'def simulate_analysis\(scan_type\):.*?return \{[^}]+\}'

# Find all matches
matches = list(re.finditer(pattern, content, re.DOTALL))
print(f"Found {len(matches)} simulate_analysis functions")

if matches:
    # Replace the FIRST occurrence with the new function
    content = content[:matches[0].start()] + new_function + content[matches[0].end():]
    
    # Remove subsequent duplicates
    for match in matches[1:]:
        # Recalculate positions after previous replacements
        matches_after = list(re.finditer(pattern, content, re.DOTALL))
        if matches_after:
            # Remove the duplicate
            content = content[:matches_after[0].start()] + content[matches_after[0].end():]
    
    print("Replaced simulate_analysis function(s)")
else:
    print("No simulate_analysis functions found")

# Now update scan_image calls to pass image_file
# Find: analysis_result = simulate_analysis(scan_type)
# Replace: analysis_result = simulate_analysis(scan_type, image_file)
content = re.sub(
    r'analysis_result = simulate_analysis\(scan_type\)',
    'analysis_result = simulate_analysis(scan_type, image_file)',
    content
)
print("Updated simulate_analysis calls to pass image_file")

# Ensure hashlib is imported at the top
if 'import hashlib' not in content:
    # Find the imports section and add hashlib
    import_pattern = r'(import random\s+)'
    if re.search(import_pattern, content):
        content = re.sub(import_pattern, r'import random\nimport hashlib\n', content, count=1)
        print("Added hashlib import")

# Write back
with open(views_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n✅ Fixed! The scan results will now be consistent for the same image.")
print("Run this script: python fix_simulate_analysis.py")
