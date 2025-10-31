"""
Download PyTorch model files for CacaoGuard
Run this script after deployment to download model files
"""
import os
import requests
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parent / 'models'
MODELS_DIR.mkdir(exist_ok=True)

# Model URLs - You'll need to upload these to a cloud storage (Google Drive, Dropbox, etc.)
MODELS = {
    'cacao_disease_resnet_state_dict.pth': 'YOUR_DISEASE_MODEL_URL_HERE',
    'cacao_pest_resnet_state_dict.pth': 'YOUR_PEST_MODEL_URL_HERE'
}

def download_file(url, destination):
    """Download a file from URL to destination"""
    print(f"Downloading {destination.name}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    block_size = 8192
    downloaded = 0
    
    with open(destination, 'wb') as f:
        for chunk in response.iter_content(block_size):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size:
                    progress = (downloaded / total_size) * 100
                    print(f"Progress: {progress:.1f}%", end='\r')
    
    print(f"\n✓ Downloaded {destination.name}")

def main():
    print("=" * 50)
    print("CacaoGuard Model Downloader")
    print("=" * 50)
    
    for model_name, url in MODELS.items():
        model_path = MODELS_DIR / model_name
        
        if model_path.exists():
            print(f"✓ {model_name} already exists")
            continue
        
        if url == 'YOUR_DISEASE_MODEL_URL_HERE' or url == 'YOUR_PEST_MODEL_URL_HERE':
            print(f"⚠ Please update the URL for {model_name} in download_models.py")
            continue
        
        try:
            download_file(url, model_path)
        except Exception as e:
            print(f"✗ Error downloading {model_name}: {e}")
    
    print("\n" + "=" * 50)
    print("Download complete!")
    print("=" * 50)

if __name__ == '__main__':
    main()
