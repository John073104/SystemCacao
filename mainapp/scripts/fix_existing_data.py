import os
import django
import uuid

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoguard.settings')
django.setup()

from mainapp.models import Order, CartItem
from django.contrib.auth.models import User

print("Fixing existing data...")

# Fix orders without order numbers
orders_without_numbers = Order.objects.filter(order_number__isnull=True) | Order.objects.filter(order_number='')

for order in orders_without_numbers:
    order.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    order.save()
    print(f"Updated order ID {order.id} with order number {order.order_number}")

print(f"Updated {orders_without_numbers.count()} orders")

# Handle cart items without users (if any)
orphaned_cart_items = CartItem.objects.filter(user__isnull=True, session_key__isnull=True)

if orphaned_cart_items.exists():
    print(f"Found {orphaned_cart_items.count()} orphaned cart items")
    
    # Option 1: Delete orphaned items
    deleted_count = orphaned_cart_items.delete()
    print(f"Deleted {deleted_count[0]} orphaned cart items")
    
    # Option 2: Assign to anonymous session (uncomment if needed)
    # for item in orphaned_cart_items:
    #     item.session_key = 'anonymous'
    #     item.save()

print("Data migration completed!")
