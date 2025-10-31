# ===============================
# NEW URL PATTERNS FOR ALL FIXES
# Add these to your existing mainapp/urls.py
# ===============================

from django.urls import path
from . import ecommerce_fixes, notifications, admin_fixes, order_fixes

# E-commerce URLs (Stock Deduction & Receipt)
ecommerce_patterns = [
    path('api/orders/complete/<str:order_id>/', ecommerce_fixes.complete_order_and_deduct_stock, name='complete_order'),
    path('api/payment/create-intent/', ecommerce_fixes.create_payment_intent, name='create_payment_intent'),
    path('api/payment/webhook/', ecommerce_fixes.payment_webhook, name='payment_webhook'),
]

# Notification URLs
notification_patterns = [
    path('api/notifications/', notifications.get_notifications, name='get_notifications'),
    path('api/notifications/<str:notification_id>/read/', notifications.mark_notification_read, name='mark_notification_read'),
    path('api/notifications/mark-all-read/', notifications.mark_all_notifications_read, name='mark_all_notifications_read'),
]

# Admin URLs (Scan History & Farm Requests)
admin_patterns = [
    path('api/admin/scan-history/', admin_fixes.get_all_scan_history, name='admin_scan_history'),
    path('api/admin/scan/<str:scan_id>/toggle/', admin_fixes.toggle_scan_visibility, name='toggle_scan'),
    path('api/admin/farm-requests/', admin_fixes.get_farm_requests, name='farm_requests'),
    path('api/admin/farm-requests/approve/', admin_fixes.approve_farm_request, name='approve_farm_request'),
    path('api/admin/farm-requests/reject/', admin_fixes.reject_farm_request, name='reject_farm_request'),
]

# Order URLs (Fix loading errors)
order_patterns = [
    path('api/orders/<str:order_id>/', order_fixes.get_order_details, name='get_order_details'),
    path('api/orders/user/', order_fixes.get_user_orders, name='get_user_orders'),
]

# Combine all patterns
all_fix_patterns = ecommerce_patterns + notification_patterns + admin_patterns + order_patterns
