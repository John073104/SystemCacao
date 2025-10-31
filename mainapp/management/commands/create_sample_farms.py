from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from mainapp.models import Farm
from decimal import Decimal

class Command(BaseCommand):
    help = 'Create sample farm data'

    def handle(self, *args, **options):
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@cacaoguard.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))

        # Sample farm data
        sample_farms = [
            {
                'name': 'Barangay Poblacion Farm',
                'municipality': 'Victoria',
                'barangay': 'Poblacion',
                'area': Decimal('4.5'),
                'trees': 520,
                'status': 'Active',
                'latitude': Decimal('13.1375'),
                'longitude': Decimal('121.2410'),
                'description': 'Primary cacao growing area with established farms',
                'contact': 'Brgy. Captain Juan Santos',
            },
            {
                'name': 'San Vicente Cacao Farm',
                'municipality': 'Victoria',
                'barangay': 'San Vicente',
                'area': Decimal('3.2'),
                'trees': 430,
                'status': 'Active',
                'latitude': Decimal('13.1500'),
                'longitude': Decimal('121.2333'),
                'description': 'Emerging farming community with modern techniques',
                'contact': 'Brgy. Captain Maria Cruz',
            },
            {
                'name': 'Macatoc Cacao Farm',
                'municipality': 'Victoria',
                'barangay': 'Macatoc',
                'area': Decimal('8.5'),
                'trees': 850,
                'status': 'Monitoring',
                'latitude': Decimal('13.1440'),
                'longitude': Decimal('121.2320'),
                'description': 'Large scale cacao production facility',
                'contact': 'Farm Manager Pedro Reyes',
            }
        ]

        for farm_data in sample_farms:
            farm, created = Farm.objects.get_or_create(
                name=farm_data['name'],
                defaults={**farm_data, 'created_by': admin_user}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created farm: {farm.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Farm already exists: {farm.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample farm data')
        )
