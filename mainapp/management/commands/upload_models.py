"""
Management command to upload ML models to Firebase Storage
"""

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from mainapp.firebase_storage import cacao_model_storage
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Upload ML models to Firebase Storage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--models-dir',
            type=str,
            default='models/',
            help='Directory containing model files'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force upload even if model already exists'
        )

    def handle(self, *args, **options):
        models_dir = options['models_dir']
        force = options['force']
        
        # Get the project root directory
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        models_path = project_root / models_dir
        
        if not models_path.exists():
            self.stdout.write(
                self.style.ERROR(f'Models directory not found: {models_path}')
            )
            return
        
        # Find all .pth files
        model_files = list(models_path.glob('*.pth'))
        
        if not model_files:
            self.stdout.write(
                self.style.WARNING('No .pth model files found')
            )
            return
        
        self.stdout.write(f'Found {len(model_files)} model files')
        
        for model_file in model_files:
            model_name = model_file.stem  # filename without extension
            
            # Check if model already exists
            if not force and cacao_model_storage.model_exists(model_name):
                self.stdout.write(
                    self.style.WARNING(f'Model {model_name} already exists. Use --force to overwrite.')
                )
                continue
            
            try:
                # Read model file
                with open(model_file, 'rb') as f:
                    model_content = ContentFile(f.read(), name=model_file.name)
                
                # Upload to Firebase Storage
                saved_path = cacao_model_storage.save_model(model_content, model_name)
                
                # Get public URL
                model_url = cacao_model_storage.get_model_url(model_name)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully uploaded {model_name} to Firebase Storage'
                    )
                )
                self.stdout.write(f'URL: {model_url}')
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to upload {model_name}: {str(e)}')
                )
        
        # List all models in storage
        self.stdout.write('\nModels in Firebase Storage:')
        models = cacao_model_storage.list_models()
        for model in models:
            self.stdout.write(f'- {model["name"]} ({model["size"]} bytes)')
            self.stdout.write(f'  URL: {model["url"]}')
