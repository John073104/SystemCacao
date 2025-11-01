# ===============================
# ECOMMERCE FIXES - Stock Deduction, Receipt & Payment
# ===============================

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from firebase_admin import firestore
from datetime import datetime
import pytz
import json
import hashlib
import base64
import requests
from . import firebase_config

# Get Firestore client from centralized config
db = firebase_config.db

# ===== FIX #1: STOCK DEDUCTION WHEN ORDER COMPLETED =====

def complete_order_and_deduct_stock(request, order_id):
    """
    Complete order and deduct stock from products
    Admin only - called when marking order as 'delivered'
    """
    try:
        # Get order from Firestore
        order_ref = db.collection('orders').document(order_id)
        order_doc = order_ref.get()
        
        if not order_doc.exists:
            return JsonResponse({'success': False, 'error': 'Order not found'})
        
        order_data = order_doc.to_dict()
        old_status = order_data.get('status')
        
        # Only deduct stock when changing to delivered status
        if request.POST.get('status') == 'delivered' and old_status != 'delivered':
            products_ref = db.collection('products')
            
            # Deduct stock for each item
            for item in order_data.get('items', []):
                product_id = item.get('product_id')
                quantity_ordered = int(item.get('quantity', 0))
                
                if product_id:
                    product_ref = products_ref.document(product_id)
                    product_doc = product_ref.get()
                    
                    if product_doc.exists:
                        product_data = product_doc.to_dict()
                        current_stock = int(product_data.get('stock_quantity', 0))
                        new_stock = max(0, current_stock - quantity_ordered)
                        
                        # Update product stock
                        product_ref.update({
                            'stock_quantity': new_stock,
                            'last_updated': datetime.now(pytz.timezone('Asia/Manila'))
                        })
                        
                        print(f"✅ Stock deducted: {product_data.get('name')} ({current_stock} → {new_stock})")
            
            # Update order status
            order_ref.update({
                'status': 'delivered',
                'completed_at': datetime.now(pytz.timezone('Asia/Manila')),
                'updated_by': request.session.get('user_email', 'admin')
            })
            
            # Send receipt to customer
            send_order_receipt(order_data)
            
            return JsonResponse({
                'success': True,
                'message': 'Order completed and stock deducted successfully'
            })
        else:
            # Just update status without stock deduction
            order_ref.update({
                'status': request.POST.get('status'),
                'updated_at': datetime.now(pytz.timezone('Asia/Manila'))
            })
            
            return JsonResponse({
                'success': True,
                'message': 'Order status updated'
            })
            
    except Exception as e:
        print(f"❌ Error completing order: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)})


# ===== FIX #2: SEND RECEIPT TO USER =====

def send_order_receipt(order_data):
    """Send email receipt to customer after order completion"""
    try:
        customer_email = order_data.get('customer_email') or order_data.get('user_email')
        order_id = order_data.get('order_id', 'N/A')
        customer_name = order_data.get('customer_first_name', 'Customer')
        
        if not customer_email:
            print("⚠️ No customer email found")
            return
        
        # Prepare receipt email
        subject = f'Order Receipt #{order_id} - CacaoGuard'
        
        # Build items list
        items_html = ""
        total = 0
        for item in order_data.get('items', []):
            item_total = float(item.get('price', 0)) * int(item.get('quantity', 0))
            total += item_total
            items_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{item.get('product_name')}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">{item.get('quantity')}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">₱{item.get('price')}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">₱{item_total:.2f}</td>
            </tr>
            """
        
        # HTML email template
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: white; padding: 30px; border: 1px solid #e5e7eb; }}
                .footer {{ background: #f9fafb; padding: 20px; text-align: center; font-size: 14px; color: #6b7280; border-radius: 0 0 10px 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .total-row {{ font-weight: bold; font-size: 18px; color: #10b981; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌿 CacaoGuard</h1>
                    <h2>Order Receipt</h2>
                </div>
                <div class="content">
                    <p>Dear {customer_name},</p>
                    <p>Thank you for your order! Your order has been successfully completed and delivered.</p>
                    
                    <h3>Order Details</h3>
                    <p><strong>Order ID:</strong> {order_id}</p>
                    <p><strong>Date:</strong> {datetime.now(pytz.timezone('Asia/Manila')).strftime('%B %d, %Y')}</p>
                    <p><strong>Customer:</strong> {customer_name}</p>
                    <p><strong>Email:</strong> {customer_email}</p>
                    
                    <h3>Items Ordered</h3>
                    <table>
                        <thead>
                            <tr style="background: #f9fafb;">
                                <th style="padding: 10px; text-align: left;">Product</th>
                                <th style="padding: 10px; text-align: center;">Qty</th>
                                <th style="padding: 10px; text-align: right;">Price</th>
                                <th style="padding: 10px; text-align: right;">Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                            <tr class="total-row">
                                <td colspan="3" style="padding: 15px; text-align: right;">Total Amount:</td>
                                <td style="padding: 15px; text-align: right;">₱{total:.2f}</td>
                            </tr>
                        </tbody>
                    </table>
                    
                    <p>If you have any questions about your order, please contact us.</p>
                    <p>Thank you for supporting local cacao farmers!</p>
                </div>
                <div class="footer">
                    <p><strong>CacaoGuard</strong> - Supporting Cacao Farmers in Oriental Mindoro</p>
                    <p>Questions? Contact us at support@cacaoguard.com</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send email
        send_mail(
            subject=subject,
            message=f"Order Receipt #{order_id}\n\nYour order has been completed!",  # Plain text fallback
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@cacaoguard.com'),
            recipient_list=[customer_email],
            html_message=html_message,
            fail_silently=True,
        )
        
        print(f"✅ Receipt sent to {customer_email}")
        
    except Exception as e:
        print(f"❌ Error sending receipt: {str(e)}")


# ===== FIX #6: PAYMENT INTEGRATION (FREE API - PAYMONGO) =====

def create_payment_intent(request):
    """
    Create payment intent using Paymongo free API
    Supports GCash, PayMaya, Credit Card
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            amount = float(data.get('amount'))
            
            # Convert to centavos (Paymongo requirement)
            amount_centavos = int(amount * 100)
            
            # Paymongo Test API Key (FREE - get from paymongo.com)
            api_key = 'sk_test_YOUR_SECRET_KEY_HERE'  # Replace with your key
            
            # Create payment intent
            url = 'https://api.paymongo.com/v1/payment_intents'
            auth_string = base64.b64encode(f'{api_key}:'.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {auth_string}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'data': {
                    'attributes': {
                        'amount': amount_centavos,
                        'payment_method_allowed': ['card', 'gcash', 'paymaya', 'grab_pay'],
                        'currency': 'PHP',
                        'description': f'CacaoGuard Order #{order_id}',
                        'statement_descriptor': 'CACAOGUARD',
                        'metadata': {
                            'order_id': order_id,
                            'user_email': request.session.get('user_email')
                        }
                    }
                }
            }
            
            response = requests.post(url, json=payload, headers=headers)
            result = response.json()
            
            if response.status_code == 200:
                payment_intent_id = result['data']['id']
                client_key = result['data']['attributes']['client_key']
                
                # Save payment intent to order
                orders_ref = db.collection('orders')
                query = orders_ref.where('order_id', '==', order_id).limit(1)
                docs = list(query.stream())
                
                if docs:
                    docs[0].reference.update({
                        'payment_intent_id': payment_intent_id,
                        'payment_status': 'pending'
                    })
                
                return JsonResponse({
                    'success': True,
                    'client_key': client_key,
                    'payment_intent_id': payment_intent_id
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result.get('errors', [{'detail': 'Payment creation failed'}])[0].get('detail')
                })
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# ===== PAYMENT WEBHOOK (to confirm payment) =====

@csrf_exempt
def payment_webhook(request):
    """Handle Paymongo payment webhooks"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            event_type = data.get('data', {}).get('attributes', {}).get('type')
            
            if event_type == 'payment.paid':
                payment_intent_id = data['data']['attributes']['data']['id']
                
                # Find and update order
                orders_ref = db.collection('orders')
                query = orders_ref.where('payment_intent_id', '==', payment_intent_id).limit(1)
                docs = list(query.stream())
                
                if docs:
                    docs[0].reference.update({
                        'payment_status': 'paid',
                        'paid_at': datetime.now(pytz.timezone('Asia/Manila'))
                    })
                    
                    print(f"✅ Payment confirmed for order")
                
            return JsonResponse({'success': True})
            
        except Exception as e:
            print(f"❌ Webhook error: {e}")
            return JsonResponse({'success': False}, status=500)
    
    return JsonResponse({'success': False}, status=405)
