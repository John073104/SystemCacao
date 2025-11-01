# ===============================
# PRODUCTION-READY USER DASHBOARD
# ===============================
# This is the ONLY userdashboard function needed
# Replace all duplicate functions in views.py with this one

from django.shortcuts import render, redirect
from django.contrib import messages
from firebase_admin import firestore
import json
import pytz
from datetime import datetime, timedelta
from .decorators import user_required
from . import firebase_config

# Get Firestore client from centralized config
db = firebase_config.db

@user_required
def userdashboard(request):
    """
    Enhanced User Dashboard with comprehensive analytics
    - Fetches orders, scans, and farm data from Firestore
    - Generates chart data for visualization
    - Handles all dashboard statistics
    """
    print("[DEBUG] Accessing User Dashboard:", request.session.get('user_email'), request.session.get('role'))
    
    # Check if user is guest (guests cannot access user dashboard)
    if request.session.get('role') == 'guest':
        messages.error(request, "Guest users cannot access user dashboard.")
        return redirect('guest_dashboard')
    
    # Get user info from session
    uid = request.session.get('uid')
    user_email = request.session.get('user_email')
    user_name = request.session.get('name')
    user_role = request.session.get('role')
    
    # Initialize timezone
    tz = pytz.timezone('Asia/Manila')
    today = datetime.now(tz)
    
    # Initialize default context
    context = {
        'name': user_name,
        'email': user_email,
        'role': user_role,
        'uid': uid,
        'current_date': today.strftime('%Y-%m-%d'),
        'current_time': today.strftime('%H:%M:%S'),
        
        # Default statistics
        'total_orders': 0,
        'total_scans': 0,
        'total_maps': 0,
        'pending_orders': 0,
        'delivered_orders': 0,
        'total_spent': 0,
        'disease_scans': 0,
        'pest_scans': 0,
        'total_farm_area': 0,
        'total_trees': 0,
        
        # Default lists
        'recent_orders': [],
        'recent_scans': [],
        'recent_farms': [],
        
        # Default chart data
        'orders_chart_data': json.dumps([]),
        'scans_chart_data': json.dumps([]),
        'scan_distribution': json.dumps({'disease': 0, 'pest': 0}),
        'monthly_chart_data': json.dumps({'labels': [], 'orders': [], 'scans': []}),
        'order_status_distribution': json.dumps({'pending': 0, 'processing': 0, 'delivered': 0, 'cancelled': 0}),
    }
    
    try:
        # ===== FETCH ORDERS DATA =====
        print("[DEBUG] Fetching orders data...")
        orders_ref = db.collection('orders')
        user_orders_query = orders_ref.where('firebase_uid', '==', uid)
        user_orders = list(user_orders_query.stream())
        
        total_orders = len(user_orders)
        pending_orders = len([o for o in user_orders if o.to_dict().get('status') == 'pending'])
        delivered_orders = len([o for o in user_orders if o.to_dict().get('status') == 'delivered'])
        total_spent = sum(float(o.to_dict().get('total_amount', 0)) for o in user_orders if o.to_dict().get('status') == 'delivered')
        
        # Get recent orders
        recent_orders = []
        for doc in sorted(user_orders, key=lambda x: x.to_dict().get('created_at', datetime.now(tz)), reverse=True)[:5]:
            order_data = doc.to_dict()
            order_data['id'] = doc.id
            if 'created_at' in order_data and order_data['created_at']:
                if hasattr(order_data['created_at'], 'seconds'):
                    order_data['created_at'] = datetime.fromtimestamp(order_data['created_at'].seconds, tz=pytz.UTC).astimezone(tz)
            recent_orders.append(order_data)
        
        # ===== FETCH SCANS DATA =====
        print("[DEBUG] Fetching scans data...")
        scans_ref = db.collection('scans')
        user_scans_query = scans_ref.where('user_id', '==', uid)
        user_scans = list(user_scans_query.stream())
        
        total_scans = len(user_scans)
        disease_scans = len([s for s in user_scans if s.to_dict().get('type') == 'disease'])
        pest_scans = len([s for s in user_scans if s.to_dict().get('type') == 'pest'])
        
        # Get recent scans
        recent_scans = []
        for doc in sorted(user_scans, key=lambda x: x.to_dict().get('timestamp', datetime.now(tz)), reverse=True)[:5]:
            scan_data = doc.to_dict()
            scan_data['id'] = doc.id
            
            # Convert confidence to percentage if stored as decimal
            confidence = scan_data.get('confidence', 0)
            if isinstance(confidence, (int, float)):
                if confidence <= 1.0:
                    scan_data['confidence'] = round(confidence * 100, 1)
                else:
                    scan_data['confidence'] = round(confidence, 1)
            
            if 'timestamp' in scan_data and scan_data['timestamp']:
                if hasattr(scan_data['timestamp'], 'seconds'):
                    scan_data['timestamp'] = datetime.fromtimestamp(scan_data['timestamp'].seconds, tz=pytz.UTC).astimezone(tz)
            
            recent_scans.append(scan_data)
        
        # ===== FETCH FARM DATA =====
        print("[DEBUG] Fetching farm data...")
        # Sample farms (from your SAMPLE_FARMS list)
        total_farm_area = 0
        total_trees = 0
        total_maps = 0
        recent_farms = []
        
        try:
            # Try to get farms from Firestore
            farms_ref = db.collection('farms')
            firebase_farms = list(farms_ref.stream())
            
            for farm_doc in firebase_farms:
                farm_data = farm_doc.to_dict()
                total_farm_area += float(farm_data.get('area', 0))
                total_trees += int(farm_data.get('trees', 0))
            
            total_maps = len(firebase_farms)
            
            # Get recent farms
            for farm_doc in firebase_farms[:3]:
                farm_data = farm_doc.to_dict()
                farm_data['id'] = farm_doc.id
                recent_farms.append(farm_data)
            
            print(f"[DEBUG] Farm totals - Maps: {total_maps}, Area: {total_farm_area}, Trees: {total_trees}")
        except Exception as farm_error:
            print(f"[ERROR] Error fetching Firebase farms: {farm_error}")
            # Continue with zero farm data if Firebase fails
        
        # ===== PREPARE CHART DATA =====
        # Orders trend (last 7 days)
        orders_chart_data = []
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            daily_orders = len([
                o for o in user_orders 
                if o.to_dict().get('created_at') and
                o.to_dict()['created_at'].astimezone(tz).date() == date.date()
            ])
            
            orders_chart_data.append({
                'date': date_str,
                'count': daily_orders,
                'label': date.strftime('%b %d')
            })
        
        # Scans trend (last 7 days)
        scans_chart_data = []
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            daily_scans = len([
                s for s in user_scans 
                if s.to_dict().get('timestamp') and
                s.to_dict()['timestamp'].astimezone(tz).date() == date.date()
            ])
            
            scans_chart_data.append({
                'date': date_str,
                'count': daily_scans,
                'label': date.strftime('%b %d')
            })
        
        # Monthly data (last 6 months)
        monthly_orders = {}
        monthly_scans = {}
        for i in range(5, -1, -1):
            month_date = today - timedelta(days=30*i)
            month_key = month_date.strftime('%b')
            monthly_orders[month_key] = 0
            monthly_scans[month_key] = 0
        
        for order in user_orders:
            order_date = order.to_dict().get('created_at')
            if order_date:
                month_key = order_date.astimezone(tz).strftime('%b')
                if month_key in monthly_orders:
                    monthly_orders[month_key] += 1
        
        for scan in user_scans:
            scan_date = scan.to_dict().get('timestamp')
            if scan_date:
                month_key = scan_date.astimezone(tz).strftime('%b')
                if month_key in monthly_scans:
                    monthly_scans[month_key] += 1
        
        monthly_chart_data = {
            'labels': list(monthly_orders.keys()),
            'orders': list(monthly_orders.values()),
            'scans': list(monthly_scans.values())
        }
        
        # Order status distribution
        cancelled_orders = len([o for o in user_orders if o.to_dict().get('status') == 'cancelled'])
        processing_orders = len([o for o in user_orders if o.to_dict().get('status') == 'processing'])
        confirmed_orders = len([o for o in user_orders if o.to_dict().get('status') == 'confirmed'])
        
        order_status_distribution = {
            'pending': pending_orders,
            'processing': processing_orders,
            'delivered': delivered_orders,
            'cancelled': cancelled_orders,
            'confirmed': confirmed_orders
        }
        
        # Scan distribution
        scan_distribution = {
            'disease': disease_scans,
            'pest': pest_scans
        }
        
        # Update context with fetched data
        context.update({
            'total_orders': total_orders,
            'total_scans': total_scans,
            'total_maps': total_maps,
            'pending_orders': pending_orders,
            'delivered_orders': delivered_orders,
            'total_spent': round(total_spent, 2),
            'disease_scans': disease_scans,
            'pest_scans': pest_scans,
            'total_farm_area': round(total_farm_area, 1),
            'total_trees': total_trees,
            'recent_orders': recent_orders,
            'recent_scans': recent_scans,
            'recent_farms': recent_farms,
            'orders_chart_data': json.dumps(orders_chart_data),
            'scans_chart_data': json.dumps(scans_chart_data),
            'scan_distribution': json.dumps(scan_distribution),
            'monthly_chart_data': json.dumps(monthly_chart_data),
            'order_status_distribution': json.dumps(order_status_distribution),
        })
        
        print("[DEBUG] User Dashboard context prepared successfully")
        
    except Exception as e:
        print(f"[ERROR] Error in userdashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        # Context already has default values, so dashboard will still render
    
    return render(request, 'user/userdashboard.html', context)
