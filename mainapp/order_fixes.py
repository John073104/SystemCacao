# ===============================
# ORDER DETAILS FIX
# FIX #5: Fix "error loading order details" in user area
# ===============================

from django.http import JsonResponse
from firebase_admin import firestore
from datetime import datetime
import pytz
import logging
from . import firebase_config

# Get Firestore client from centralized config
db = firebase_config.db
logger = logging.getLogger(__name__)

def get_order_details(request, order_id):
    """
    Get order details with proper error handling
    Fixes the "error loading order details" issue
    """
    try:
        # Check if Firebase is initialized
        if db is None:
            return JsonResponse({
                'success': False,
                'error': 'Database connection unavailable. Please try again later.'
            }, status=503)
        
        uid = request.session.get('uid')
        user_email = request.session.get('user_email') or request.session.get('email')
        
        if not uid or not user_email:
            return JsonResponse({
                'success': False,
                'error': 'Please log in to view order details'
            }, status=401)
        
        # Try to find order by document ID first
        order_ref = db.collection('orders').document(order_id)
        order_doc = order_ref.get()
        
        # If not found by document ID, try by order_id field
        if not order_doc.exists:
            query = db.collection('orders').where('order_id', '==', order_id).limit(1)
            docs = list(query.stream())
            
            if not docs:
                logger.error(f"Order not found: {order_id}")
                return JsonResponse({
                    'success': False,
                    'error': 'Order not found'
                }, status=404)
            
            order_doc = docs[0]
        
        # Get order data
        order_data = order_doc.to_dict()
        order_data['id'] = order_doc.id
        
        # Verify ownership
        owner_uid = order_data.get('firebase_uid') or order_data.get('user_id')
        owner_email = order_data.get('customer_email') or order_data.get('user_email')
        
        if owner_uid and owner_uid != uid and owner_email and owner_email != user_email:
            logger.warning(f"Unauthorized access attempt to order {order_id} by {user_email}")
            return JsonResponse({
                'success': False,
                'error': 'Access denied'
            }, status=403)
        
        # Format timestamps properly
        if 'created_at' in order_data:
            if hasattr(order_data['created_at'], 'seconds'):
                # Firestore timestamp
                timestamp = datetime.fromtimestamp(order_data['created_at'].seconds, tz=pytz.UTC)
                order_data['formatted_date'] = timestamp.astimezone(pytz.timezone('Asia/Manila')).strftime('%B %d, %Y %I:%M %p')
            elif isinstance(order_data['created_at'], str):
                # String timestamp
                order_data['formatted_date'] = order_data['created_at']
            else:
                order_data['formatted_date'] = 'N/A'
        else:
            order_data['formatted_date'] = 'N/A'
        
        # Ensure items exist
        if 'items' not in order_data or not isinstance(order_data['items'], list):
            order_data['items'] = []
        
        # Calculate totals
        subtotal = 0
        for item in order_data['items']:
            item_total = float(item.get('price', 0)) * int(item.get('quantity', 0))
            item['item_total'] = item_total
            subtotal += item_total
        
        order_data['subtotal'] = subtotal
        order_data['total'] = order_data.get('total_amount', subtotal)
        
        # Add shipping address if missing
        if 'shipping_address' not in order_data:
            order_data['shipping_address'] = 'Not provided'
        
        # Add payment method if missing
        if 'payment_method' not in order_data:
            order_data['payment_method'] = 'Cash on Delivery'
        
        # Add payment status
        if 'payment_status' not in order_data:
            order_data['payment_status'] = 'pending'
        
        logger.info(f"Order details loaded successfully: {order_id}")
        
        return JsonResponse({
            'success': True,
            'order': order_data
        })
        
    except Exception as e:
        logger.exception(f"Error loading order details for {order_id}")
        return JsonResponse({
            'success': False,
            'error': f'Error loading order details: {str(e)}'
        }, status=500)


def get_user_orders(request):
    """Get all orders for current user with error handling"""
    try:
        # Check if Firebase is initialized
        if db is None:
            return JsonResponse({
                'success': False,
                'error': 'Database connection unavailable. Please try again later.'
            }, status=503)
        
        uid = request.session.get('uid')
        user_email = request.session.get('user_email') or request.session.get('email')
        
        if not uid or not user_email:
            return JsonResponse({
                'success': False,
                'error': 'Please log in to view orders'
            }, status=401)
        
        # Get orders from Firestore
        orders_ref = db.collection('orders')
        
        # Try multiple query methods for compatibility
        queries = [
            orders_ref.where('firebase_uid', '==', uid),
            orders_ref.where('user_id', '==', uid),
            orders_ref.where('customer_email', '==', user_email),
        ]
        
        orders = []
        order_ids_seen = set()
        
        for query in queries:
            try:
                docs = query.stream()
                for doc in docs:
                    if doc.id not in order_ids_seen:
                        order_data = doc.to_dict()
                        order_data['id'] = doc.id
                        
                        # Format timestamp
                        if 'created_at' in order_data and hasattr(order_data['created_at'], 'seconds'):
                            timestamp = datetime.fromtimestamp(order_data['created_at'].seconds, tz=pytz.UTC)
                            order_data['formatted_date'] = timestamp.astimezone(pytz.timezone('Asia/Manila')).strftime('%b %d, %Y')
                        
                        orders.append(order_data)
                        order_ids_seen.add(doc.id)
            except Exception as query_error:
                logger.warning(f"Query failed: {str(query_error)}")
                continue
        
        # Sort by date (newest first)
        orders.sort(key=lambda x: x.get('created_at', 0), reverse=True)
        
        return JsonResponse({
            'success': True,
            'orders': orders,
            'total': len(orders)
        })
        
    except Exception as e:
        logger.exception("Error getting user orders")
        return JsonResponse({
            'success': False,
            'error': f'Error loading orders: {str(e)}'
        }, status=500)
