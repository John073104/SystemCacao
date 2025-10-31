from django.core.management.base import BaseCommand
from django.conf import settings
from mainapp.models import ScanResult
import os

class Command(BaseCommand):
    help = 'Clean up orphaned scan image files'
    
    def handle(self, *args, **options):
        from mainapp.views import cleanup_orphaned_files
        
        deleted_count = cleanup_orphaned_files()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully cleaned up {deleted_count} orphaned files'
            )
        )
