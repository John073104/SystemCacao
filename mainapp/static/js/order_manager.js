/**
 * ORDER MANAGEMENT FIX
 * Handles order loading errors and payment integration
 * FIX #5: Error loading order details
 * FIX #6: Payment function
 */

class OrderManager {
    constructor() {
        this.currentOrder = null;
        this.init();
    }

    init() {
        console.log('✅ Order Manager initialized');
    }

    /**
     * Load order details with proper error handling
     */
    async loadOrderDetails(orderId) {
        try {
            this.showLoading('Loading order details...');
            
            const response = await fetch(`/api/orders/${orderId}/`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            this.hideLoading();
            
            if (data.success) {
                this.currentOrder = data.order;
                this.displayOrderDetails(data.order);
            } else {
                this.showError(data.error || 'Failed to load order details');
            }
        } catch (error) {
            this.hideLoading();
            console.error('❌ Error loading order details:', error);
            this.showError('Network error. Please check your connection and try again.');
        }
    }

    /**
     * Display order details in UI
     */
    displayOrderDetails(order) {
        const container = document.getElementById('order-details-container');
        
        if (!container) {
            console.error('Order details container not found');
            return;
        }
        
        const statusColors = {
            'pending': 'yellow',
            'paid': 'blue',
            'confirmed': 'indigo',
            'processing': 'purple',
            'shipped': 'cyan',
            'delivered': 'green',
            'cancelled': 'red'
        };
        
        const statusColor = statusColors[order.status] || 'gray';
        
        container.innerHTML = `
            <div class="bg-white rounded-lg shadow-md p-6">
                <!-- Order Header -->
                <div class="flex justify-between items-start mb-6 border-b pb-4">
                    <div>
                        <h2 class="text-2xl font-bold text-gray-800">Order #${order.order_id || order.id}</h2>
                        <p class="text-gray-600 mt-1">${order.formatted_date || 'N/A'}</p>
                    </div>
                    <span class="px-4 py-2 rounded-full text-sm font-semibold bg-${statusColor}-100 text-${statusColor}-800">
                        ${order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                    </span>
                </div>
                
                <!-- Customer Info -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    <div>
                        <h3 class="font-semibold text-gray-700 mb-2">Customer Information</h3>
                        <p class="text-gray-600">${order.customer_first_name || ''} ${order.customer_last_name || ''}</p>
                        <p class="text-gray-600">${order.customer_email || order.user_email || ''}</p>
                        <p class="text-gray-600">${order.phone_number || ''}</p>
                    </div>
                    <div>
                        <h3 class="font-semibold text-gray-700 mb-2">Shipping Address</h3>
                        <p class="text-gray-600">${order.shipping_address || 'Not provided'}</p>
                    </div>
                </div>
                
                <!-- Order Items -->
                <h3 class="text-lg font-semibold mb-3">Order Items</h3>
                <div class="space-y-3 mb-6">
                    ${order.items && order.items.length > 0 ? order.items.map(item => `
                        <div class="flex items-center justify-between border-b pb-3">
                            <div class="flex items-center space-x-4 flex-1">
                                <div>
                                    <p class="font-medium text-gray-800">${item.product_name || 'Unknown Product'}</p>
                                    <p class="text-sm text-gray-600">Qty: ${item.quantity} × ₱${parseFloat(item.price || 0).toFixed(2)}</p>
                                </div>
                            </div>
                            <p class="font-semibold text-gray-800">₱${parseFloat(item.item_total || 0).toFixed(2)}</p>
                        </div>
                    `).join('') : '<p class="text-gray-500">No items</p>'}
                </div>
                
                <!-- Order Total -->
                <div class="border-t pt-4">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-gray-600">Subtotal:</span>
                        <span class="font-semibold">₱${parseFloat(order.subtotal || order.total || 0).toFixed(2)}</span>
                    </div>
                    <div class="flex justify-between items-center mb-4">
                        <span class="text-xl font-semibold text-gray-700">Total Amount:</span>
                        <span class="text-3xl font-bold text-green-600">₱${parseFloat(order.total || order.total_amount || 0).toFixed(2)}</span>
                    </div>
                    
                    <!-- Payment Method -->
                    <div class="bg-gray-50 p-4 rounded-lg mb-4">
                        <p class="text-sm text-gray-600">Payment Method: <span class="font-semibold">${order.payment_method || 'Cash on Delivery'}</span></p>
                        <p class="text-sm text-gray-600">Payment Status: <span class="font-semibold ${order.payment_status === 'paid' ? 'text-green-600' : 'text-yellow-600'}">${order.payment_status || 'Pending'}</span></p>
                    </div>
                    
                    <!-- Action Buttons -->
                    ${order.status === 'pending' && order.payment_status !== 'paid' ? `
                        <button onclick="orderManager.initiatePayment('${order.order_id || order.id}', ${order.total || order.total_amount})" 
                                class="w-full bg-green-500 text-white py-3 rounded-lg hover:bg-green-600 transition-colors flex items-center justify-center space-x-2">
                            <i class="fas fa-credit-card"></i>
                            <span>Proceed to Payment</span>
                        </button>
                    ` : order.status === 'delivered' ? `
                        <div class="bg-green-50 p-4 rounded-lg text-center">
                            <i class="fas fa-check-circle text-green-600 text-4xl mb-2"></i>
                            <p class="text-green-700 font-semibold">Order Delivered Successfully!</p>
                            <p class="text-sm text-green-600 mt-1">Thank you for your purchase!</p>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    /**
     * Initiate payment process
     */
    async initiatePayment(orderId, amount) {
        try {
            this.showLoading('Processing payment...');
            
            const response = await fetch('/api/payment/create-intent/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({
                    order_id: orderId,
                    amount: amount
                })
            });
            
            const data = await response.json();
            
            this.hideLoading();
            
            if (data.success) {
                // Open payment gateway (Paymongo)
                this.showSuccess('Redirecting to payment gateway...');
                
                // In production, you would redirect to Paymongo payment page
                // For now, show success message
                setTimeout(() => {
                    alert(`Payment Intent Created!\nClient Key: ${data.client_key}\n\nIn production, this would open the Paymongo payment form.`);
                }, 500);
            } else {
                this.showError(data.error || 'Payment initialization failed');
            }
        } catch (error) {
            this.hideLoading();
            console.error('Payment error:', error);
            this.showError('Payment processing error. Please try again.');
        }
    }

    /**
     * Load user orders list
     */
    async loadUserOrders() {
        try {
            const response = await fetch('/api/orders/user/');
            const data = await response.json();
            
            if (data.success) {
                this.displayOrdersList(data.orders);
            } else {
                this.showError(data.error);
            }
        } catch (error) {
            console.error('Error loading orders:', error);
            this.showError('Failed to load orders');
        }
    }

    /**
     * Display orders list
     */
    displayOrdersList(orders) {
        const container = document.getElementById('orders-list-container');
        
        if (!container) return;
        
        if (orders.length === 0) {
            container.innerHTML = `
                <div class="text-center py-12">
                    <i class="fas fa-shopping-bag text-6xl text-gray-300 mb-4"></i>
                    <p class="text-gray-500 text-lg">No orders yet</p>
                    <a href="/user/marketplace/" class="mt-4 inline-block bg-green-500 text-white px-6 py-2 rounded-lg hover:bg-green-600">
                        Start Shopping
                    </a>
                </div>
            `;
            return;
        }
        
        container.innerHTML = orders.map(order => `
            <div class="bg-white rounded-lg shadow-md p-6 mb-4 hover:shadow-lg transition-shadow">
                <div class="flex justify-between items-start">
                    <div>
                        <h3 class="font-semibold text-lg">Order #${order.order_id || order.id}</h3>
                        <p class="text-sm text-gray-600">${order.formatted_date || 'N/A'}</p>
                        <p class="text-sm text-gray-600 mt-1">${order.items ? order.items.length : 0} items</p>
                    </div>
                    <div class="text-right">
                        <p class="font-bold text-lg text-green-600">₱${parseFloat(order.total_amount || 0).toFixed(2)}</p>
                        <span class="text-xs px-2 py-1 rounded-full ${this.getStatusBadgeClass(order.status)}">
                            ${order.status || 'Pending'}
                        </span>
                    </div>
                </div>
                <div class="mt-4">
                    <button onclick="orderManager.loadOrderDetails('${order.id}')" 
                            class="text-green-600 hover:text-green-700 font-semibold text-sm">
                        View Details →
                    </button>
                </div>
            </div>
        `).join('');
    }

    getStatusBadgeClass(status) {
        const classes = {
            'pending': 'bg-yellow-100 text-yellow-800',
            'confirmed': 'bg-blue-100 text-blue-800',
            'processing': 'bg-purple-100 text-purple-800',
            'shipped': 'bg-cyan-100 text-cyan-800',
            'delivered': 'bg-green-100 text-green-800',
            'cancelled': 'bg-red-100 text-red-800'
        };
        return classes[status] || 'bg-gray-100 text-gray-800';
    }

    /**
     * UI Helper Methods
     */
    showLoading(message = 'Loading...') {
        const loadingHtml = `
            <div id="loading-indicator" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                <div class="bg-white rounded-lg p-6 flex flex-col items-center">
                    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mb-4"></div>
                    <p class="text-gray-700">${message}</p>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', loadingHtml);
    }

    hideLoading() {
        const loader = document.getElementById('loading-indicator');
        if (loader) loader.remove();
    }

    showError(message) {
        this.showAlert(message, 'error');
    }

    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    showAlert(message, type = 'info') {
        const colors = {
            'error': { bg: 'bg-red-100', border: 'border-red-400', text: 'text-red-700', icon: 'fa-exclamation-circle' },
            'success': { bg: 'bg-green-100', border: 'border-green-400', text: 'text-green-700', icon: 'fa-check-circle' },
            'info': { bg: 'bg-blue-100', border: 'border-blue-400', text: 'text-blue-700', icon: 'fa-info-circle' }
        };
        
        const color = colors[type] || colors['info'];
        
        const alertHtml = `
            <div class="fixed top-4 right-4 ${color.bg} border ${color.border} ${color.text} px-4 py-3 rounded shadow-lg z-50 max-w-md animate-slide-in">
                <div class="flex items-start">
                    <i class="fas ${color.icon} mr-3 mt-1"></i>
                    <div class="flex-1">
                        <p class="font-semibold">${type.charAt(0).toUpperCase() + type.slice(1)}</p>
                        <p class="text-sm">${message}</p>
                    </div>
                    <button onclick="this.parentElement.parentElement.remove()" class="ml-4 ${color.text} hover:opacity-75">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', alertHtml);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            const alerts = document.querySelectorAll('.fixed.top-4.right-4');
            alerts.forEach(alert => alert.remove());
        }, 5000);
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Initialize order manager
const orderManager = new OrderManager();

// Export for use in templates
window.orderManager = orderManager;
