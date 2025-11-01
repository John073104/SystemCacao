# ===============================
# SCAN HISTORY & FARM REQUEST FIXES
# FIX #2: Show/Hide scan history
# FIX #3: Farm request approval
# ===============================

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from firebase_admin import firestore
from datetime import datetime
import pytz
from .notifications import create_notification
from . import firebase_config

# Get Firestore client from centralized config
db = firebase_config.db

# ===== FIX #2: SCAN HISTORY WITH SHOW/HIDE =====

def get_all_scan_history(request):
    """
    Get all scan history for admin with show/hide functionality
    """
    try:
        # Check if user is admin
        if request.session.get('role') != 'admin':
            return JsonResponse({'success': False, 'error': 'Admin access required'})
        
        # Get all scans from Firestore
        scans_ref = db.collection('scans')
        query = scans_ref.order_by('timestamp', direction=firestore.Query.DESCENDING)
        
        scans = []
        for doc in query.stream():
            scan_data = doc.to_dict()
            scan_data['id'] = doc.id
            
            # Format timestamp
            if 'timestamp' in scan_data and hasattr(scan_data['timestamp'], 'seconds'):
                timestamp = datetime.fromtimestamp(scan_data['timestamp'].seconds, tz=pytz.UTC)
                scan_data['formatted_date'] = timestamp.astimezone(pytz.timezone('Asia/Manila')).strftime('%b %d, %Y %I:%M %p')
            
            # Get user details
            user_id = scan_data.get('user_id')
            if user_id and user_id != 'guest':
                user_email = scan_data.get('user_email', 'Unknown')
                user_name = scan_data.get('user_name', user_email.split('@')[0])
            else:
                user_name = 'Guest User'
                user_email = 'guest'
            
            scan_data['display_name'] = user_name
            scan_data['display_email'] = user_email
            
            # Add visibility flag (default: visible)
            if 'hidden' not in scan_data:
                scan_data['hidden'] = False
            
            scans.append(scan_data)
        
        return JsonResponse({
            'success': True,
            'scans': scans,
            'total': len(scans)
        })
        
    except Exception as e:
        print(f"Error getting scan history: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def toggle_scan_visibility(request, scan_id):
    """Toggle scan visibility (show/hide)"""
    if request.method == 'POST':
        try:
            # Check admin access
            if request.session.get('role') != 'admin':
                return JsonResponse({'success': False, 'error': 'Admin access required'})
            
            scan_ref = db.collection('scans').document(scan_id)
            scan_doc = scan_ref.get()
            
            if not scan_doc.exists:
                return JsonResponse({'success': False, 'error': 'Scan not found'})
            
            scan_data = scan_doc.to_dict()
            current_hidden = scan_data.get('hidden', False)
            
            # Toggle visibility
            scan_ref.update({
                'hidden': not current_hidden,
                'updated_at': datetime.now(pytz.timezone('Asia/Manila')),
                'updated_by': request.session.get('user_email', 'admin')
            })
            
            return JsonResponse({
                'success': True,
                'hidden': not current_hidden,
                'message': f"Scan {'hidden' if not current_hidden else 'visible'}"
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})


# ===== FIX #3: FARM REQUEST APPROVAL =====

def get_farm_requests(request):
    """Get all pending farm requests for admin"""
    try:
        # Check admin access
        if request.session.get('role') != 'admin':
            return JsonResponse({'success': False, 'error': 'Admin access required'})
        
        # Get farm requests from Firestore
        requests_ref = db.collection('farm_requests')
        query = requests_ref.order_by('submitted_at', direction=firestore.Query.DESCENDING)
        
        farm_requests = []
        for doc in query.stream():
            request_data = doc.to_dict()
            request_data['id'] = doc.id
            
            # Format timestamp
            if 'submitted_at' in request_data and hasattr(request_data['submitted_at'], 'seconds'):
                timestamp = datetime.fromtimestamp(request_data['submitted_at'].seconds, tz=pytz.UTC)
                request_data['formatted_date'] = timestamp.astimezone(pytz.timezone('Asia/Manila')).strftime('%b %d, %Y %I:%M %p')
            
            farm_requests.append(request_data)
        
        return JsonResponse({
            'success': True,
            'requests': farm_requests,
            'total': len(farm_requests),
            'pending': len([r for r in farm_requests if r.get('status') == 'pending'])
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def approve_farm_request(request):
    """Approve a farm request and create farm location"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            request_id = data.get('request_id')
            
            # Check admin access
            if request.session.get('role') != 'admin':
                return JsonResponse({'success': False, 'error': 'Admin access required'})
            
            # Get farm request
            request_ref = db.collection('farm_requests').document(request_id)
            request_doc = request_ref.get()
            
            if not request_doc.exists:
                return JsonResponse({'success': False, 'error': 'Request not found'})
            
            request_data = request_doc.to_dict()
            
            # Check if already processed
            if request_data.get('status') != 'pending':
                return JsonResponse({'success': False, 'error': 'Request already processed'})
            
            # Create farm in farms collection
            farm_data = {
                'name': request_data.get('farm_name'),
                'owner': request_data.get('owner_name'),
                'contact': request_data.get('contact'),
                'municipality': request_data.get('municipality'),
                'barangay': request_data.get('barangay'),
                'latitude': request_data.get('latitude'),
                'longitude': request_data.get('longitude'),
                'area': request_data.get('area'),
                'description': request_data.get('description', ''),
                'status': 'Active',
                'user_id': request_data.get('user_id'),
                'approved_by': request.session.get('user_email'),
                'created_at': datetime.now(pytz.timezone('Asia/Manila'))
            }
            
            # Add to farms collection
            farm_ref = db.collection('farms').add(farm_data)
            farm_id = farm_ref[1].id
            
            # Update request status
            request_ref.update({
                'status': 'approved',
                'approved_at': datetime.now(pytz.timezone('Asia/Manila')),
                'approved_by': request.session.get('user_email'),
                'farm_id': farm_id
            })
            
            # Create notification for user
            user_id = request_data.get('user_id')
            if user_id:
                create_notification(
                    user_id=user_id,
                    title='Farm Request Approved ✓',
                    message=f'Your farm "{request_data.get("farm_name")}" has been approved and added to the map!',
                    notification_type='farm_approved',
                    related_id=farm_id
                )
            
            print(f"✅ Farm request approved: {request_data.get('farm_name')}")
            
            return JsonResponse({
                'success': True,
                'message': 'Farm request approved successfully',
                'farm_id': farm_id
            })
            
        except Exception as e:
            print(f"❌ Error approving farm request: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})


@csrf_exempt
def reject_farm_request(request):
    """Reject a farm request"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            request_id = data.get('request_id')
            reason = data.get('reason', 'Does not meet requirements')
            
            # Check admin access
            if request.session.get('role') != 'admin':
                return JsonResponse({'success': False, 'error': 'Admin access required'})
            
            # Get farm request
            request_ref = db.collection('farm_requests').document(request_id)
            request_doc = request_ref.get()
            
            if not request_doc.exists:
                return JsonResponse({'success': False, 'error': 'Request not found'})
            
            request_data = request_doc.to_dict()
            
            # Update request status
            request_ref.update({
                'status': 'rejected',
                'rejected_at': datetime.now(pytz.timezone('Asia/Manila')),
                'rejected_by': request.session.get('user_email'),
                'rejection_reason': reason
            })
            
            # Create notification for user
            user_id = request_data.get('user_id')
            if user_id:
                create_notification(
                    user_id=user_id,
                    title='Farm Request Rejected',
                    message=f'Your farm request "{request_data.get("farm_name")}" was rejected. Reason: {reason}',
                    notification_type='farm_rejected',
                    related_id=request_id
                )
            
            print(f"⚠️ Farm request rejected: {request_data.get('farm_name')}")
            
            return JsonResponse({
                'success': True,
                'message': 'Farm request rejected'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})
