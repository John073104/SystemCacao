from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .fix_urls import all_fix_patterns

urlpatterns = [
    # ===== PUBLIC/COMMON PAGES =====
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('team/', views.team, name='team'),
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('unauthorized/', views.unauthorized, name='unauthorized'),

    # ===== AUTHENTICATION =====
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('firebase-login/', views.firebase_login, name='firebase_login'),
    path('send-welcome-email/', views.send_welcome_email, name='send_welcome_email'),
    
    # Debug endpoint
    path('debug/session/', views.debug_session, name='debug_session'),

    # ===== ADMIN URLS =====
    # Admin Dashboard
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Admin Ecommerce Management
    path('admin/ecommerce/', views.admin_ecommerce, name='admin_ecommerce'),
    path('admin/products/', views.admin_products, name='admin_products'),
    path('admin/products/add/', views.admin_add_product, name='admin_add_product'),
    path('admin/products/edit/<str:product_id>/', views.admin_edit_product, name='admin_edit_product'),
    path('admin/products/delete/<str:product_id>/', views.admin_delete_product, name='admin_delete_product'),

    # Admin Order Management
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('admin/orders/<str:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('admin/orders/<str:order_id>/delete/', views.delete_order, name='delete_order'),
    path('admin/pending-orders/', views.admin_pending_orders, name='admin_pending_orders'),
    path('api/update-order-status/<str:order_id>/', views.update_order_status, name='update_order_status'),

    # Admin Reports & Analytics
    path('admin/reports/', views.admin_reports, name='admin_reports'),
    path('admin/reports/print/<int:year>/<int:month>/', views.print_monthly_report, name='print_monthly_report'),

    # Admin Image Analysis
    path('admin/image-analysis/', views.image_analysis, name='image_analysis'),
    path('admin/delete-scan/<str:scan_id>/', views.delete_scan, name='delete_scan'),
    path('admin/toggle-scan/<str:scan_id>/', views.toggle_scan_visibility, name='toggle_scan_visibility'),
    path('admin/export-scan-data/', views.export_scan_data, name='export_scan_data'),
    path('admin/print-preview/', views.print_preview, name='print_preview'),
    path('admin/export-pdf/', views.export_pdf, name='export_pdf'),

    # Admin Farm Management
    path('admin/farm-location/', views.farm_location, name='farm_location'),

    # Admin Debug & Utilities
    path('admin/debug-firestore/', views.debug_firestore_collections, name='debug_firestore_collections'),
    path('admin/fix-scan-timestamps/', views.admin_fix_scan_timestamps, name='admin_fix_scan_timestamps'),
    path('admin/user-management/', views.admin_user_management, name='admin_user_management'),
    path('admin/user-management/hide/<str:user_id>/', views.hide_user, name='hide_user'),
    path('admin/user-management/unhide/<str:user_id>/', views.unhide_user, name='unhide_user'),

    # ===== USER URLS =====
    # User Dashboard
    path('dashboard/', views.userdashboard, name='userdashboard'),
    path('dashboard-api/', views.dashboard_api, name='dashboard_api'),
    path('dashboard/report/', views.generate_dashboard_report, name='dashboard_report'),

    # User Profile Management
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/image/upload/', views.profile_image_upload_ajax, name='profile_image_upload_ajax'),
    path('profile/image/delete/', views.delete_profile_image_view, name='delete_profile_image'),
    path('accounts/', views.accounts, name='accounts'),

    # User Marketplace
    path('marketplace/', views.marketplace, name='marketplace'),
    path('product/<str:product_id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),

    # User Orders
    path('checkout/', views.checkout_view, name='checkout'),
    path('order-confirmation/<str:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('orders/', views.user_orders, name='user_orders'),
    path('orders/<str:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<str:order_id>/receipt/', views.order_receipt, name='order_receipt'),
    path('orders/<str:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('orders/<str:order_id>/hide/', views.hide_order, name='hide_order'),
    path('orders/<str:order_id>/delete/', views.delete_user_order, name='delete_user_order'),
    path('orders/<str:order_id>/unhide/', views.unhide_order, name='unhide_order'),
    path('orders/hidden/', views.hidden_orders, name='hidden_orders'),

    # User Scan & Diagnosis
    path('scan/', views.scan_diagnose, name='scan_diagnose'),
    path('scan-image/', views.scan_image, name='scan_image'),
    path('scan-history/', views.scan_history, name='scan_history'),
    path('scan/details/<str:scan_id>/', views.scan_details, name='scan_details'),
    path('history/toggle/', views.toggle_history, name='toggle_history'),
    path('history/delete/<str:scan_id>/', views.delete_user_scan, name='delete_user_scan'),

    # User Farm Mapping
    path('farm-mapping/', views.farm_mapping, name='farm_mapping'),

    # User Chatbot
    path('chat/', views.chat, name='chat'),

    # ===== GUEST URLS =====
    # Guest Dashboard
    path('guest/dashboard/', views.guest_dashboard, name='guest_dashboard'),

    # Guest Marketplace
    path('guest/marketplace/', views.guest_marketplace, name='guest_marketplace'),
    path('products/<str:product_id>/', views.guest_product_detail, name='guest_product_detail'),

    # Guest Farm Mapping
    path('guest/farm-mapping/', views.guest_farm_mapping, name='guest_farm_mapping'),

    # Guest Scanning
    path('guest-scan-image/', views.guest_scan_image, name='guest_scan_image'),
    path('reset-guest-scans/', views.reset_guest_scans, name='reset_guest_scans'),
    path('get-scan-history/', views.get_scan_history, name='get_scan_history'),

    # ===== API ENDPOINTS =====
    # General APIs
    path('api/monthly-data/', views.get_monthly_data, name='get_monthly_data'),

    # Scan APIs
    path('api/scan-history/', views.scan_history_api, name='scan_history_api'),
    path('api/scan-image/', views.scan_image, name='api_scan_image'),

    # Farm APIs
    path('api/farm-data/', views.get_farm_data_api, name='get_farm_data_api'),
    path('api/farm-image/upload/', views.upload_farm_image, name='upload_farm_image'),
    path('api/farm-image/delete/', views.delete_farm_image, name='delete_farm_image'),
    path('api/admin/farms-firebase/', views.api_farms_firebase, name='api_farms_firebase'),
    path('api/user/farm-request-firebase/', views.api_user_farm_request_firebase, name='api_user_farm_request_firebase'),
    path('api/public/farms-firebase/', views.api_public_farms_firebase, name='api_public_farms_firebase'),
    path('api/admin/approve-farm/', views.api_approve_farm_request, name='api_approve_farm_request'),
    path('api/admin/reject-farm/', views.api_reject_farm_request, name='api_reject_farm_request'),

    # Notification APIs
    path('api/notifications/', views.api_get_notifications, name='api_get_notifications'),
    path('api/notifications/mark-read/', views.api_mark_notification_read, name='api_mark_notification_read'),
    path('api/notifications/mark-all-read/', views.api_mark_all_notifications_read, name='api_mark_all_notifications_read'),

    # Guest APIs
    path('api/guest/scan/', views.guest_scan_diagnose, name='guest_scan_image_api'),
    path('api/guest/limits/', views.get_daily_scan_limits, name='get_guest_scan_limits'),
]


# Append fixed patterns
urlpatterns += all_fix_patterns

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 403 Handler
handler403 = 'mainapp.views.custom_403'
