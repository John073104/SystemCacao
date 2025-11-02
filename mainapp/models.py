from django.db import models
   
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=254, blank=True)

    def __str__(self):
        return self.user.username
    


    
# ===============================
# Scan
# ===============================
from django.db import models
from django.contrib.auth import get_user_model

from django.conf import settings



class ScanResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    scan_type = models.CharField(max_length=10, choices=[('disease', 'Disease'), ('pest', 'Pest')], default='disease')

    image_name = models.CharField(max_length=255)
    disease_class = models.CharField(max_length=100, default="Unknown")
    disease_confidence = models.FloatField(default=0.0)
    pest_class = models.CharField(max_length=100, default="Unknown")
    pest_confidence = models.FloatField(default=0.0)
    primary_class = models.CharField(max_length=100, default="Unknown")
    primary_confidence = models.FloatField(default=0.0)
    recommendations = models.JSONField(default=list)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.primary_class} ({self.timestamp})"


# ===============================
# End Scan
# ===============================
    
# ===============================
# Category, Product, and Order models
# ===============================     
from django.db import models
from django.contrib.auth import get_user_model


from django.utils import timezone
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

# class Product(models.Model):
#     PRODUCT_TYPES = [
#         ('fresh_cacao', 'Fresh Cacao Fruit'),
#         ('dried_beans', 'Dried Cacao Beans'),
#         ('cacao_powder', 'Cacao Powder'),
#         ('chocolate', 'Chocolate Products'),
#         ('cacao_butter', 'Cacao Butter'),
#         ('cacao_nibs', 'Cacao Nibs'),
#     ]
    
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=200)
#     description = models.TextField()
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     stock_quantity = models.IntegerField(default=0)
#     unit = models.CharField(max_length=20, default='kg')  # kg, pieces, etc.
#     images = models.JSONField(default=list)  # Store multiple image URLs
#     is_active = models.BooleanField(default=True)
#     featured = models.BooleanField(default=False)
#     origin = models.CharField(max_length=100, blank=True)  # Farm/region origin
#     harvest_date = models.DateField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return self.name
    
#     @property
#     def main_image(self):
#         return self.images[0] if self.images else '/static/images/placeholder.jpg'

# class Cart(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

# class CartItem(models.Model):
#     # Temporarily allow null values for the user field
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

#     product = models.ForeignKey('Product', on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return f"{self.quantity} x {self.product.name}"
    
#     class Meta:
#         unique_together = ['user', 'product']  # Prevent duplicate items per user

# from django.db import models




# class Order(models.Model):
#     PENDING = 'pending'
#     PROCESSING = 'processing'
#     COMPLETED = 'completed'
#     CANCELLED = 'cancelled'

#     STATUS_CHOICES = [
#         (PENDING, 'Pending'),
#         (PROCESSING, 'Processing'),
#         (COMPLETED, 'Completed'),
#         (CANCELLED, 'Cancelled'),
#     ]
    
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     shipping_address = models.TextField()
#     phone_number = models.CharField(max_length=20)
#     notes = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     order_number = models.CharField(max_length=100, default='0000')
    
    
#     def __str__(self):
#         return f"Order {self.id} - {self.user.email} - {self.status}"


# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
#     product_id = models.CharField(max_length=100)
#     product_name = models.CharField(max_length=255)
#     quantity = models.PositiveIntegerField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
    
#     def __str__(self):
#         return f"{self.quantity} x {self.product_name}"

# ===============================
# End Ecommerce
# ===============================

# from django.db import models
# from django.contrib.auth import get_user_model

# from django.utils import timezone

# class Product(models.Model):
#     """Products in marketplace added by admin"""
#     name = models.CharField(max_length=200)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     stock = models.PositiveIntegerField(default=0)
#     image = models.ImageField(upload_to='products/', blank=True, null=True)
#     category = models.CharField(max_length=100, default='General')
#     is_active = models.BooleanField(default=True)
#     created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'is_staff': True})

#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         ordering = ['-created_at']
    
#     def __str__(self):
#         return self.name


class CacaoFarm(models.Model):
    """Cacao farms for mapping in Oriental Mindoro"""
    name = models.CharField(max_length=200)
    owner = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=20, blank=True)
    province = models.CharField(max_length=100, default='Oriental Mindoro')
    municipality = models.CharField(max_length=100)
    barangay = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    area_hectares = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.municipality}"




# class CartItem(models.Model):
#     """Cart items for e-commerce"""
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#     added_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.product.name} x {self.quantity}"

# import uuid
# from django.db import models
# from django.contrib.auth import get_user_model



# class Order(models.Model):
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('confirmed', 'Confirmed'),
#         ('processing', 'Processing'),
#         ('shipped', 'Shipped'),
#         ('delivered', 'Delivered'),
#         ('cancelled', 'Cancelled'),
#     ]
#     firebase_uid = models.CharField(max_length=128) 
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     order_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     shipping_address = models.TextField()
#     phone_number = models.CharField(max_length=15)
#     notes = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def save(self, *args, **kwargs):
#         if not self.order_number:
#             # Generate a unique order number
#             self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"Order {self.order_number} by {self.user.username}"

#     class Meta:
#         ordering = ['-created_at']

# class OrderItem(models.Model):
#     firebase_uid = models.CharField(max_length=128) 
#     order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     def __str__(self):
#         return f"{self.quantity} x {self.product.name}"

#     @property
#     def total_price(self):
#         return self.quantity * self.price

# ===============================
# Farm
# ===============================

from django.db import models
from django.contrib.auth import get_user_model


from django.utils import timezone
import uuid

class Farm(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Monitoring', 'Monitoring'),
        ('Needs Attention', 'Needs Attention'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    municipality = models.CharField(max_length=100)
    barangay = models.CharField(max_length=100)
    area = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Area in hectares")
    trees = models.PositiveIntegerField(null=True, blank=True, help_text="Number of cacao trees")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    description = models.TextField(blank=True)
    contact = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'is_staff': True})

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} - {self.municipality}"
    
    @property
    def coordinates(self):
        if self.latitude and self.longitude:
            return [float(self.latitude), float(self.longitude)]
        return None

class FarmImage(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='farm_images/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Image for {self.farm.name}"

class FarmRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requested_farms')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_farms')
    farm_name = models.CharField(max_length=200)
    location = models.CharField(max_length=300)
    contact = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(default=timezone.now)
    reviewed_at = models.DateTimeField(null=True, blank=True)
   
    
    class Meta:
        ordering = ['-submitted_at']
        
    def __str__(self):
        return f"Request: {self.farm_name} by {self.user.username}"
    
# ===============================
# User
# ===============================
    
from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image

class CustomUser(AbstractUser):

    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
        ('guest', 'Guest'),
    ]
    uid = models.CharField(max_length=128, blank=True)  # Firebase UID
    role = models.CharField(max_length=20, default='User') 
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    
    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.photo:
            img = Image.open(self.photo.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.photo.path)
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

# REMOVED DUPLICATE UserProfile - Already defined at line 14

class UserLoginLog(models.Model):
    
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-login_time']


# NOTE: Category, Product, Cart models already defined earlier in file (lines 72-200)
# Only Order, OrderItem, CartItem models defined below to avoid duplicates

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firebase_id = models.CharField(max_length=20, default='TEMP_ID') 
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    phone_number = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    session_key = models.CharField(max_length=100, null=True, blank=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    
    @property
    def total_price(self):
        return self.quantity * self.price

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def total_price(self):
        return self.quantity * self.product.price
    

