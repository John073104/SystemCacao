from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from mainapp.models import Farm, Category, Product
from decimal import Decimal
import uuid

class Command(BaseCommand):
    help = 'Setup initial database with sample data'

    def handle(self, *args, **options):
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@cacaoguard.com',
                password='admin123'
            )
            self.stdout.write(
                self.style.SUCCESS('Created admin user (username: admin, password: admin123)')
            )
        else:
            admin_user = User.objects.get(username='admin')
            self.stdout.write(
                self.style.WARNING('Admin user already exists')
            )

        # Create sample categories
        categories_data = [
            {'name': 'Fresh Cacao', 'description': 'Fresh cacao fruits and pods'},
            {'name': 'Processed Cacao', 'description': 'Dried beans, powder, and other processed products'},
            {'name': 'Chocolate Products', 'description': 'Finished chocolate products'},
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )

        # Create sample farms
        farms_data = [
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

        for farm_data in farms_data:
            farm, created = Farm.objects.get_or_create(
                name=farm_data['name'],
                defaults={**farm_data, 'created_by': admin_user}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created farm: {farm.name}')
                )

        # Create sample products
        fresh_category = Category.objects.get(name='Fresh Cacao')
        processed_category = Category.objects.get(name='Processed Cacao')

        products_data = [
            {
                'name': 'Fresh Cacao Pods',
                'description': 'Fresh cacao pods directly from the farm',
                'category': fresh_category,
                'product_type': 'fresh_cacao',
                'price': Decimal('150.00'),
                'stock_quantity': 100,
                'unit': 'pieces',
                'origin': 'Victoria, Oriental Mindoro',
            },
            {
                'name': 'Dried Cacao Beans',
                'description': 'Premium quality dried cacao beans',
                'category': processed_category,
                'product_type': 'dried_beans',
                'price': Decimal('800.00'),
                'stock_quantity': 50,
                'unit': 'kg',
                'origin': 'Victoria, Oriental Mindoro',
            }
        ]

        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={**product_data, 'created_by': admin_user}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created product: {product.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Database setup completed successfully!')
        )
