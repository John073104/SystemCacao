# CacaoGuard Models Directory

This directory contains the PyTorch model files for disease and pest detection.

## Model Files Required:
- `cacao_disease_resnet_state_dict.pth` (~463 MB)
- `cacao_pest_resnet_state_dict.pth` (~463 MB)

## For Local Development:
Models should already be in this directory.

## For Render Deployment:
1. Upload model files to cloud storage (Google Drive, Dropbox, etc.)
2. Get direct download links
3. Update URLs in `download_models.py`
4. Run: `python download_models.py` after deployment

## Note:
These files are excluded from git due to their large size (927 MB total).
