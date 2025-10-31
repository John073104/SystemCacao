import os
from pathlib import Path

# Create static directories
BASE_DIR = Path(__file__).resolve().parent
static_dir = BASE_DIR / 'static'
images_dir = static_dir / 'images'

# Create directories if they don't exist
static_dir.mkdir(exist_ok=True)
images_dir.mkdir(exist_ok=True)

# Create a simple default avatar (you can replace this with an actual image file)
default_avatar_content = '''<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="50" fill="#e5e7eb"/>
  <circle cx="50" cy="35" r="15" fill="#9ca3af"/>
  <ellipse cx="50" cy="75" rx="20" ry="15" fill="#9ca3af"/>
</svg>'''

# Write default avatar
with open(images_dir / 'default-avatar.svg', 'w') as f:
    f.write(default_avatar_content)

print("Static files created successfully!")
print(f"Created: {static_dir}")
print(f"Created: {images_dir}")
print(f"Created: {images_dir / 'default-avatar.svg'}")
