from django.contrib import admin
from .models import Product, CacaoFarm, ScanResult, CartItem, Order, OrderItem

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'get_stock']

    def get_stock(self, obj):
        return getattr(obj, 'stock', getattr(obj, 'stock_quantity', 'N/A'))
    get_stock.short_description = 'Stock'

    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']
    



@admin.register(CacaoFarm)
class CacaoFarmAdmin(admin.ModelAdmin):
    list_display = ['name', 'municipality', 'barangay', 'province', 'is_active']
    list_filter = ['province', 'municipality', 'is_active']
    search_fields = ['name', 'owner']


@admin.register(ScanResult)
class ScanResultAdmin(admin.ModelAdmin):
    readonly_fields = ['timestamp']
    list_display = ['user', 'primary_class', 'primary_confidence', 'timestamp']
    list_filter = ['scan_type', 'timestamp', 'primary_class']
    search_fields = ['user__username', 'primary_class', 'disease_class', 'pest_class']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['get_user', 'product', 'quantity']

    def get_user(self, obj):
        return obj.user
    get_user.short_description = 'User'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['get_order_number', 'user', 'status', 'total_amount', 'created_at']

    def get_order_number(self, obj):
        return getattr(obj, 'order_number', f"ORD-{obj.id}")
    get_order_number.short_description = 'Order Number'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    list_filter = ['product']
