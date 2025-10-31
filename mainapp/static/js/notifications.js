/**
 * NOTIFICATION MANAGER
 * Handles notification bell icon and real-time updates
 * FIX #7: Add notifications with bell icon
 */

class NotificationManager {
    constructor() {
        this.notifications = [];
        this.unreadCount = 0;
        this.checkInterval = 30000; // Check every 30 seconds
        this.init();
    }

    init() {
        console.log('✅ Notification Manager initialized');
        this.loadNotifications();
        
        // Auto-refresh notifications
        setInterval(() => this.loadNotifications(), this.checkInterval);
        
        // Setup event listeners
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Close notification panel when clicking outside
        document.addEventListener('click', (event) => {
            const panel = document.getElementById('notification-panel');
            const bell = event.target.closest('.notification-bell');
            
            if (panel && !bell && panel.classList.contains('show')) {
                panel.classList.remove('show');
            }
        });
    }

    async loadNotifications() {
        try {
            const response = await fetch('/api/notifications/');
            const data = await response.json();
            
            if (data.success) {
                this.notifications = data.notifications;
                this.unreadCount = data.unread_count;
                this.updateBadge();
                
                // Only render if panel is open
                const panel = document.getElementById('notification-panel');
                if (panel && panel.classList.contains('show')) {
                    this.renderNotifications();
                }
            }
        } catch (error) {
            console.error('❌ Error loading notifications:', error);
        }
    }

    updateBadge() {
        const badge = document.getElementById('notification-badge');
        if (!badge) return;
        
        if (this.unreadCount > 0) {
            badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
            badge.style.display = 'flex';
            
            // Pulse animation for new notifications
            badge.classList.add('animate-pulse');
            setTimeout(() => badge.classList.remove('animate-pulse'), 2000);
        } else {
            badge.style.display = 'none';
        }
    }

    renderNotifications() {
        const list = document.getElementById('notification-list');
        if (!list) return;
        
        if (this.notifications.length === 0) {
            list.innerHTML = `
                <div class="p-8 text-center text-gray-500">
                    <i class="fas fa-bell-slash text-4xl mb-2"></i>
                    <p>No notifications</p>
                </div>
            `;
            return;
        }
        
        list.innerHTML = this.notifications.map(notif => `
            <div class="notification-item ${!notif.read ? 'unread' : ''}" 
                 onclick="notificationManager.markAsRead('${notif.id}', '${notif.related_id || ''}', '${notif.type}')">
                <div class="flex items-start space-x-3 p-4">
                    <i class="fas fa-${this.getIcon(notif.type)} ${this.getIconColor(notif.type)} mt-1 text-lg"></i>
                    <div class="flex-1">
                        <p class="font-semibold text-gray-800 text-sm">${notif.title}</p>
                        <p class="text-sm text-gray-600 mt-1">${notif.message}</p>
                        <p class="text-xs text-gray-400 mt-2">${notif.time_ago}</p>
                    </div>
                    ${!notif.read ? '<span class="w-2 h-2 bg-blue-500 rounded-full mt-2"></span>' : ''}
                </div>
            </div>
        `).join('');
    }

    getIcon(type) {
        const icons = {
            'order_completed': 'check-circle',
            'payment_success': 'credit-card',
            'farm_approved': 'check-double',
            'farm_rejected': 'times-circle',
            'system': 'info-circle',
            'info': 'bell'
        };
        return icons[type] || 'bell';
    }

    getIconColor(type) {
        const colors = {
            'order_completed': 'text-green-600',
            'payment_success': 'text-blue-600',
            'farm_approved': 'text-green-600',
            'farm_rejected': 'text-red-600',
            'system': 'text-gray-600',
            'info': 'text-blue-600'
        };
        return colors[type] || 'text-gray-600';
    }

    async markAsRead(notificationId, relatedId, type) {
        try {
            const response = await fetch(`/api/notifications/${notificationId}/read/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });
            
            if (response.ok) {
                await this.loadNotifications();
                
                // Navigate to related content if applicable
                this.handleNotificationClick(type, relatedId);
            }
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }

    handleNotificationClick(type, relatedId) {
        if (!relatedId) return;
        
        // Navigate based on notification type
        switch (type) {
            case 'order_completed':
            case 'payment_success':
                window.location.href = `/user/orders/${relatedId}/`;
                break;
            case 'farm_approved':
            case 'farm_rejected':
                window.location.href = `/user/farms/${relatedId}/`;
                break;
        }
    }

    async markAllAsRead() {
        try {
            const response = await fetch('/api/notifications/mark-all-read/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });
            
            if (response.ok) {
                await this.loadNotifications();
            }
        } catch (error) {
            console.error('Error marking all as read:', error);
        }
    }

    togglePanel() {
        const panel = document.getElementById('notification-panel');
        if (!panel) return;
        
        panel.classList.toggle('show');
        
        // Load notifications when panel opens
        if (panel.classList.contains('show')) {
            this.renderNotifications();
        }
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

// Initialize notification manager
const notificationManager = new NotificationManager();

// Global functions for use in templates
function toggleNotifications() {
    notificationManager.togglePanel();
}

function markAllAsRead() {
    notificationManager.markAllAsRead();
}

// Export for use in other modules
window.notificationManager = notificationManager;
window.toggleNotifications = toggleNotifications;
window.markAllAsRead = markAllAsRead;
