from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fix migration issues by cleaning up database'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check if tables exist and drop problematic ones
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name LIKE 'mainapp_%';
            """)
            
            tables = cursor.fetchall()
            
            # Drop tables that might cause conflicts
            problematic_tables = [
                'mainapp_cartitem',
                'mainapp_product', 
                'mainapp_order',
                'mainapp_orderitem',
                'mainapp_scanresult'
            ]
            
            for table_name in problematic_tables:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
                    self.stdout.write(
                        self.style.SUCCESS(f'Dropped table: {table_name}')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Could not drop {table_name}: {e}')
                    )
            
            # Clear migration history for mainapp
            try:
                cursor.execute("""
                    DELETE FROM django_migrations 
                    WHERE app = 'mainapp';
                """)
                self.stdout.write(
                    self.style.SUCCESS('Cleared migration history for mainapp')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'Could not clear migration history: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Database cleanup completed. Run makemigrations and migrate now.')
        )
