"""
Download PyTorch model files for CacaoGuard
Run this script after deployment to download model files
"""
import os
import requests
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parent / 'models'
MODELS_DIR.mkdir(exist_ok=True)

# Model URLs - Google Drive direct download links
MODELS = {
    'cacao_disease_resnet_state_dict.pth': 'https://drive.google.com/uc?export=download&id=1Qe5-6qqUuz8Tz9ygbuhKjqZAHYqku0dC',
    'cacao_pest_resnet_state_dict.pth': 'https://drive.google.com/uc?export=download&id=1CnLqRFDnURggYAVAdMPJU9HdKH4Uf3T5'
}

def download_file(url, destination):
    """Download a file from URL to destination"""
    print(f"Downloading {destination.name}...")
    
    # Handle Google Drive download with confirmation
    session = requests.Session()
    response = session.get(url, stream=True)
    
    # Check for Google Drive virus scan warning
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            params = {'confirm': value}
            response = session.get(url, params=params, stream=True)
            break
    
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
        
        try:
            download_file(url, model_path)
        except Exception as e:
            print(f"✗ Error downloading {model_name}: {e}")
    
    print("\n" + "=" * 50)
    print("Download complete!")
    print("=" * 50)

if __name__ == '__main__':
    main()
