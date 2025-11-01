# ===============================
# NOTIFICATION SYSTEM - Bell Icon & Profile
# FIX #7: Add notifications with bell icon
# ===============================

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import firestore
from datetime import datetime, timedelta
import pytz
from . import firebase_config

# Get Firestore client from centralized config
db = firebase_config.db

def get_notifications(request):
    """Get all notifications for logged-in user"""
    try:
        uid = request.session.get('uid')
        user_email = request.session.get('user_email')
        
        if not uid:
            return JsonResponse({'success': False, 'error': 'Not authenticated'})
        
        # Get notifications from Firestore
        notifications_ref = db.collection('notifications')
        query = notifications_ref.where('user_id', '==', uid).order_by('created_at', direction=firestore.Query.DESCENDING).limit(50)
        
        notifications = []
        unread_count = 0
        
        for doc in query.stream():
            notif_data = doc.to_dict()
            notif_data['id'] = doc.id
            
            # Format timestamp
            if 'created_at' in notif_data and hasattr(notif_data['created_at'], 'seconds'):
                created_at = datetime.fromtimestamp(notif_data['created_at'].seconds, tz=pytz.UTC)
                notif_data['time_ago'] = get_time_ago(created_at)
                notif_data['formatted_time'] = created_at.astimezone(pytz.timezone('Asia/Manila')).strftime('%b %d, %Y %I:%M %p')
            
            notifications.append(notif_data)
            
            if not notif_data.get('read', False):
                unread_count += 1
        
        return JsonResponse({
            'success': True,
            'notifications': notifications,
            'unread_count': unread_count
        })
        
    except Exception as e:
        print(f"Error getting notifications: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    if request.method == 'POST':
        try:
            uid = request.session.get('uid')
            if not uid:
                return JsonResponse({'success': False, 'error': 'Not authenticated'})
            
            # Update notification
            notif_ref = db.collection('notifications').document(notification_id)
            notif_doc = notif_ref.get()
            
            if not notif_doc.exists:
                return JsonResponse({'success': False, 'error': 'Notification not found'})
            
            notif_data = notif_doc.to_dict()
            
            # Verify ownership
            if notif_data.get('user_id') != uid:
                return JsonResponse({'success': False, 'error': 'Unauthorized'})
            
            # Mark as read
            notif_ref.update({
                'read': True,
                'read_at': datetime.now(pytz.timezone('Asia/Manila'))
            })
            
            return JsonResponse({'success': True, 'message': 'Notification marked as read'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})


@csrf_exempt
def mark_all_notifications_read(request):
    """Mark all notifications as read for current user"""
    if request.method == 'POST':
        try:
            uid = request.session.get('uid')
            if not uid:
                return JsonResponse({'success': False, 'error': 'Not authenticated'})
            
            # Get all unread notifications
            notifications_ref = db.collection('notifications')
            query = notifications_ref.where('user_id', '==', uid).where('read', '==', False)
            
            # Update all to read
            batch = db.batch()
            for doc in query.stream():
                batch.update(doc.reference, {
                    'read': True,
                    'read_at': datetime.now(pytz.timezone('Asia/Manila'))
                })
            
            batch.commit()
            
            return JsonResponse({'success': True, 'message': 'All notifications marked as read'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})


def create_notification(user_id, title, message, notification_type='info', related_id=None):
    """
    Create a new notification for a user
    
    Types: 'order_completed', 'payment_success', 'farm_approved', 'farm_rejected', 'info'
    """
    try:
        notification_data = {
            'user_id': user_id,
            'title': title,
            'message': message,
            'type': notification_type,
            'related_id': related_id,
            'read': False,
            'created_at': datetime.now(pytz.timezone('Asia/Manila'))
        }
        
        db.collection('notifications').add(notification_data)
        print(f"✅ Notification created: {title} for user {user_id}")
        
    except Exception as e:
        print(f"❌ Error creating notification: {str(e)}")


def get_time_ago(timestamp):
    """Get human-readable time difference"""
    now = datetime.now(pytz.UTC)
    if timestamp.tzinfo is None:
        timestamp = pytz.UTC.localize(timestamp)
    
    diff = now - timestamp
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"
