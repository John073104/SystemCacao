# CacaoGuard Database Data Dictionary

## Database Overview

**Database Type**: Firebase Firestore (NoSQL Cloud Database)  
**Platform**: Google Cloud Platform  
**Location**: Multi-region (us-central1)  
**Access**: Firebase Admin SDK  

---

## Collections Schema

### 1. **users** Collection

Stores user account information and authentication data.

| Field Name | Data Type | Required | Description | Example |
|------------|-----------|----------|-------------|---------|
| `uid` | String | Yes | Firebase Authentication User ID (Primary Key) | "xY9kL2mP4nQ8rT5v" |
| `email` | String | Yes | User's email address (unique) | "farmer@example.com" |
| `name` | String | Yes | Full name of the user | "Juan Dela Cruz" |
| `role` | String | Yes | User access level | "user", "admin", "guest" |
| `phone` | String | No | Contact phone number | "+639171234567" |
| `address` | String | No | Default shipping address | "123 Main St, Calapan City" |
| `profile_image` | String | No | URL to profile photo (Cloudinary) | "https://res.cloudinary.com/..." |
| `created_at` | Timestamp | Yes | Account creation date | 2025-01-15T10:30:00Z |
| `last_login` | Timestamp | No | Last successful login | 2025-12-08T08:15:00Z |
| `is_active` | Boolean | Yes | Account status | true, false |
| `email_verified` | Boolean | Yes | Email verification status | true, false |

**Indexes:**
- `email` (Ascending)
- `role` (Ascending)
- `created_at` (Descending)

**Sample Document:**
```json
{
  "uid": "xY9kL2mP4nQ8rT5v",
  "email": "farmer@cacaoguard.com",
  "name": "Juan Dela Cruz",
  "role": "user",
  "phone": "+639171234567",
  "address": "Poblacion, Victoria, Oriental Mindoro",
  "profile_image": "https://res.cloudinary.com/driikw8gl/image/upload/...",
  "created_at": "2025-01-15T10:30:00Z",
  "last_login": "2025-12-08T08:15:00Z",
  "is_active": true,
  "email_verified": true
}
```

---

### 2. **products** Collection

Stores marketplace product listings and inventory.

| Field Name | Data Type | Required | Description | Example |
|------------|-----------|----------|-------------|---------|
| `id` | String | Auto | Firestore Document ID (Primary Key) | "prod_ABC123XYZ" |
| `name` | String | Yes | Product name | "Premium Dried Cacao Beans" |
| `category` | String | Yes | Product category | "dried_beans" |
| `product_type` | String | Yes | Specific product type | "dried_beans", "fresh_cacao", etc. |
| `price` | Number | Yes | Price in Philippine Pesos | 350.00 |
| `stock` | Number | Yes | Available quantity | 120 |
| `sku` | String | No | Stock Keeping Unit code | "DCB-001-2024" |
| `description` | String | Yes | Detailed product description | "Fermented and sun-dried..." |
| `specifications` | Object | No | Product specs (weight, origin, etc.) | {"weight": "1kg", "origin": "Victoria"} |
| `images` | Array | Yes | Product image URLs (Cloudinary) | ["https://res.cloudinary.com/..."] |
| `featured` | Boolean | No | Featured on homepage | true, false |
| `is_active` | Boolean | Yes | Product availability | true, false |
| `low_stock_threshold` | Number | No | Alert when stock below this | 10 |
| `seller_id` | String | No | Admin/seller user ID | "admin_12345" |
| `created_at` | Timestamp | Yes | Product creation date | 2025-11-20T14:00:00Z |
| `updated_at` | Timestamp | Yes | Last modification date | 2025-12-05T09:30:00Z |
| `total_sold` | Number | No | Total units sold | 45 |
| `rating` | Number | No | Average customer rating (1-5) | 4.7 |
| `reviews_count` | Number | No | Number of customer reviews | 12 |

**Indexes:**
- `category` (Ascending), `is_active` (Ascending)
- `created_at` (Descending)
- `price` (Ascending)

**Sample Document:**
```json
{
  "id": "prod_ABC123XYZ",
  "name": "Premium Dried Cacao Beans",
  "category": "Dried Beans",
  "product_type": "dried_beans",
  "price": 350.00,
  "stock": 120,
  "sku": "DCB-001-2024",
  "description": "Fermented and sun-dried cacao beans from Victoria farms. Perfect for chocolate making.",
  "specifications": {
    "weight": "1kg",
    "origin": "Victoria, Oriental Mindoro",
    "processing": "Fermented 5 days, sun-dried",
    "moisture": "7%"
  },
  "images": [
    "https://res.cloudinary.com/driikw8gl/image/upload/v1/products/cacao-beans-1.jpg",
    "https://res.cloudinary.com/driikw8gl/image/upload/v1/products/cacao-beans-2.jpg"
  ],
  "featured": true,
  "is_active": true,
  "low_stock_threshold": 10,
  "seller_id": "admin_12345",
  "created_at": "2025-11-20T14:00:00Z",
  "updated_at": "2025-12-05T09:30:00Z",
  "total_sold": 45,
  "rating": 4.7,
  "reviews_count": 12
}
```

---

### 3. **orders** Collection

Stores customer purchase orders and transaction history.

| Field Name | Data Type | Required | Description | Example |
|------------|-----------|----------|-------------|---------|
| `id` | String | Auto | Firestore Document ID (Primary Key) | "order_XYZ789ABC" |
| `order_id` | String | Yes | Human-readable order number | "ORD-20251208-001" |
| `user_id` | String | Yes | Firebase UID of customer | "xY9kL2mP4nQ8rT5v" |
| `user_email` | String | Yes | Customer email | "customer@example.com" |
| `user_name` | String | Yes | Customer full name | "Maria Santos" |
| `items` | Array | Yes | Ordered products with details | [{product_id, name, quantity, price}] |
| `subtotal` | Number | Yes | Total before shipping | 1250.00 |
| `shipping_cost` | Number | Yes | Delivery fee | 100.00 |
| `total_amount` | Number | Yes | Final amount to pay | 1350.00 |
| `status` | String | Yes | Order status | "pending", "confirmed", "shipped", "delivered", "cancelled" |
| `payment_method` | String | Yes | Payment type | "cod", "gcash", "bank_transfer" |
| `shipping_address` | Object | Yes | Delivery location details | {street, barangay, city, province, postal} |
| `phone_number` | String | Yes | Contact for delivery | "+639171234567" |
| `notes` | String | No | Special delivery instructions | "Call before delivery" |
| `shipping_distance` | Number | No | Distance from warehouse (km) | 45.2 |
| `courier` | String | No | Delivery service name | "LBC", "J&T Express" |
| `tracking_number` | String | No | Shipment tracking code | "TRACK123456789" |
| `estimated_delivery` | Timestamp | No | Expected delivery date | 2025-12-15T00:00:00Z |
| `created_at` | Timestamp | Yes | Order placement date | 2025-12-08T10:30:00Z |
| `updated_at` | Timestamp | Yes | Last status change | 2025-12-08T14:45:00Z |
| `confirmed_at` | Timestamp | No | When admin confirmed | 2025-12-08T11:00:00Z |
| `shipped_at` | Timestamp | No | When marked as shipped | 2025-12-09T09:00:00Z |
| `delivered_at` | Timestamp | No | When customer received | 2025-12-12T16:30:00Z |
| `cancelled_at` | Timestamp | No | When order was cancelled | null |
| `cancellation_reason` | String | No | Why order was cancelled | "Out of stock" |

**Indexes:**
- `user_id` (Ascending), `created_at` (Descending)
- `status` (Ascending)
- `order_id` (Ascending)

**Sample Document:**
```json
{
  "id": "order_XYZ789ABC",
  "order_id": "ORD-20251208-001",
  "user_id": "xY9kL2mP4nQ8rT5v",
  "user_email": "maria@example.com",
  "user_name": "Maria Santos",
  "items": [
    {
      "product_id": "prod_ABC123",
      "name": "Dried Cacao Beans",
      "quantity": 3,
      "price": 350.00,
      "subtotal": 1050.00
    },
    {
      "product_id": "prod_DEF456",
      "name": "Cacao Nibs",
      "quantity": 2,
      "price": 100.00,
      "subtotal": 200.00
    }
  ],
  "subtotal": 1250.00,
  "shipping_cost": 100.00,
  "total_amount": 1350.00,
  "status": "shipped",
  "payment_method": "cod",
  "shipping_address": {
    "street": "123 Main Street",
    "barangay": "Poblacion",
    "city": "Calapan",
    "province": "Oriental Mindoro",
    "postal_code": "5200"
  },
  "phone_number": "+639171234567",
  "notes": "Call 30 minutes before delivery",
  "shipping_distance": 45.2,
  "courier": "J&T Express",
  "tracking_number": "TRACK123456789",
  "estimated_delivery": "2025-12-15T00:00:00Z",
  "created_at": "2025-12-08T10:30:00Z",
  "updated_at": "2025-12-09T09:15:00Z",
  "confirmed_at": "2025-12-08T11:00:00Z",
  "shipped_at": "2025-12-09T09:00:00Z",
  "delivered_at": null,
  "cancelled_at": null,
  "cancellation_reason": null
}
```

---

### 4. **scans** Collection

Stores disease and pest detection scan results.

| Field Name | Data Type | Required | Description | Example |
|------------|-----------|----------|-------------|---------|
| `id` | String | Auto | Firestore Document ID (Primary Key) | "scan_ABC123DEF456" |
| `scan_id` | String | Yes | Unique scan identifier (UUID) | "550e8400-e29b-41d4-a716-446655440000" |
| `user_id` | String | Yes | Firebase UID of scanner | "xY9kL2mP4nQ8rT5v" |
| `user_email` | String | Yes | Email of scanner | "farmer@example.com" |
| `user_name` | String | Yes | Name of scanner | "Juan Dela Cruz" |
| `user_type` | String | Yes | Scanner account type | "user", "admin", "guest" |
| `type` | String | Yes | Scan type | "disease", "pest" |
| `image_url` | String | Yes | Uploaded image URL (Cloudinary) | "https://res.cloudinary.com/..." |
| `image_hash` | String | Yes | MD5 hash of image content | "5d41402abc4b2a76b9719d911017c592" |
| `result` | String | Yes | Detection result class | "Black Pod Rot Disease", "Aphids", "Healthy" |
| `confidence` | Number | Yes | AI confidence score (0-1) | 0.87 |
| `recommendations` | Array | Yes | Treatment suggestions | ["Remove infected pods", "Apply fungicide"] |
| `description` | String | No | Detailed explanation | "Black Pod Rot is caused by..." |
| `description_tagalog` | String | No | Filipino translation | "Ang Black Pod Rot ay..." |
| `farm_id` | String | No | Associated farm location | "farm_XYZ123" |
| `timestamp` | Timestamp | Yes | When scan was performed | 2025-12-08T14:30:00Z |
| `location` | Object | No | GPS coordinates | {latitude: 13.1234, longitude: 121.5678} |
| `device_info` | String | No | Scanner device details | "Chrome 120, Windows 10" |
| `processing_time` | Number | No | AI analysis duration (ms) | 2350 |

**Indexes:**
- `user_id` (Ascending), `timestamp` (Descending)
- `type` (Ascending)
- `image_hash` (Ascending)
- `result` (Ascending)

**Sample Document:**
```json
{
  "id": "scan_ABC123DEF456",
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "xY9kL2mP4nQ8rT5v",
  "user_email": "farmer@cacaoguard.com",
  "user_name": "Juan Dela Cruz",
  "user_type": "user",
  "type": "disease",
  "image_url": "https://res.cloudinary.com/driikw8gl/image/upload/v1/scans/scan_12345.jpg",
  "image_hash": "5d41402abc4b2a76b9719d911017c592",
  "result": "Black Pod Rot Disease",
  "confidence": 0.87,
  "recommendations": [
    "Remove and destroy infected pods immediately",
    "Improve drainage and air circulation",
    "Apply copper-based fungicides",
    "Harvest ripe pods promptly"
  ],
  "description": "Black Pod Rot Disease is caused by Phytophthora species fungi...",
  "description_tagalog": "Ang Black Pod Rot Disease ay dulot ng Phytophthora fungi...",
  "farm_id": "farm_victoria_001",
  "timestamp": "2025-12-08T14:30:00Z",
  "location": {
    "latitude": 13.1854,
    "longitude": 121.3098
  },
  "device_info": "Chrome 120.0.0, Windows 10",
  "processing_time": 2350
}
```

---

### 5. **farms** Collection

Stores farm location data and metadata for mapping feature.

| Field Name | Data Type | Required | Description | Example |
|------------|-----------|----------|-------------|---------|
| `id` | String | Auto | Firestore Document ID (Primary Key) | "farm_ABC123XYZ" |
| `name` | String | Yes | Farm name | "Barangay Poblacion Cacao Farm" |
| `municipality` | String | Yes | Municipality location | "Victoria", "Calapan", "Naujan" |
| `barangay` | String | Yes | Barangay/village | "Poblacion", "San Vicente" |
| `area` | Number | Yes | Farm size in hectares | 4.5 |
| `trees` | Number | Yes | Number of cacao trees | 520 |
| `status` | String | Yes | Farm operational status | "active", "inactive", "under_maintenance" |
| `lat` | Number | Yes | Latitude coordinate | 13.1854 |
| `lng` | Number | Yes | Longitude coordinate | 121.3098 |
| `description` | String | No | Farm details | "Main production farm with organic certification" |
| `contact_person` | String | No | Farm manager name | "Pedro Garcia" |
| `contact_number` | String | No | Contact phone | "+639171234567" |
| `images` | Array | No | Farm photos (Cloudinary URLs) | ["https://res.cloudinary.com/..."] |
| `owner_id` | String | No | Farm owner user ID | "xY9kL2mP4nQ8rT5v" |
| `created_at` | Timestamp | Yes | When farm was added | 2025-11-15T10:00:00Z |
| `updated_at` | Timestamp | Yes | Last modification date | 2025-12-01T14:30:00Z |
| `last_inspection` | Timestamp | No | Recent farm visit date | 2025-11-28T09:00:00Z |
| `yield_last_harvest` | Number | No | Previous harvest in kg | 850.5 |
| `certifications` | Array | No | Farm certifications | ["Organic", "Fair Trade"] |

**Indexes:**
- `municipality` (Ascending)
- `status` (Ascending)
- `owner_id` (Ascending), `created_at` (Descending)

**Sample Document:**
```json
{
  "id": "farm_victoria_001",
  "name": "Barangay Poblacion Cacao Farm",
  "municipality": "Victoria",
  "barangay": "Poblacion",
  "area": 4.5,
  "trees": 520,
  "status": "active",
  "lat": 13.1854,
  "lng": 121.3098,
  "description": "Main production farm with organic certification. Established 2018.",
  "contact_person": "Pedro Garcia",
  "contact_number": "+639171234567",
  "images": [
    "https://res.cloudinary.com/driikw8gl/image/upload/v1/farms/farm_001_1.jpg",
    "https://res.cloudinary.com/driikw8gl/image/upload/v1/farms/farm_001_2.jpg"
  ],
  "owner_id": "xY9kL2mP4nQ8rT5v",
  "created_at": "2025-11-15T10:00:00Z",
  "updated_at": "2025-12-01T14:30:00Z",
  "last_inspection": "2025-11-28T09:00:00Z",
  "yield_last_harvest": 850.5,
  "certifications": ["Organic", "Fair Trade"]
}
```

---

### 6. **notifications** Collection

Stores user notifications for system events and updates.

| Field Name | Data Type | Required | Description | Example |
|------------|-----------|----------|-------------|---------|
| `id` | String | Auto | Firestore Document ID (Primary Key) | "notif_ABC123" |
| `user_id` | String | Yes | Recipient Firebase UID | "xY9kL2mP4nQ8rT5v" |
| `title` | String | Yes | Notification title | "Order Shipped" |
| `message` | String | Yes | Notification content | "Your order #ORD-001 has been shipped" |
| `type` | String | Yes | Notification category | "info", "success", "warning", "error", "order_status" |
| `read` | Boolean | Yes | Read status | true, false |
| `order_id` | String | No | Related order reference | "order_XYZ789" |
| `scan_id` | String | No | Related scan reference | "scan_ABC123" |
| `metadata` | Object | No | Additional data | {courier: "J&T", tracking: "TRACK123"} |
| `created_at` | Timestamp | Yes | Notification creation time | 2025-12-09T09:15:00Z |
| `read_at` | Timestamp | No | When user read notification | 2025-12-09T10:30:00Z |
| `expires_at` | Timestamp | No | Auto-delete after this date | 2025-12-16T00:00:00Z |

**Indexes:**
- `user_id` (Ascending), `created_at` (Descending)
- `user_id` (Ascending), `read` (Ascending)

**Sample Document:**
```json
{
  "id": "notif_ABC123XYZ",
  "user_id": "xY9kL2mP4nQ8rT5v",
  "title": "Order Shipped",
  "message": "Your order #ORD-20251208-001 has been shipped via J&T Express. Track: TRACK123456789",
  "type": "order_status",
  "read": false,
  "order_id": "order_XYZ789ABC",
  "scan_id": null,
  "metadata": {
    "courier": "J&T Express",
    "tracking_number": "TRACK123456789",
    "estimated_delivery": "2025-12-15"
  },
  "created_at": "2025-12-09T09:15:00Z",
  "read_at": null,
  "expires_at": "2025-12-16T00:00:00Z"
}
```

---

## Enumeration Values

### User Roles
- `user` - Regular registered user (farmer/buyer)
- `admin` - System administrator with full access
- `guest` - Non-registered visitor (limited features)

### Product Categories
- `fresh_cacao` - Fresh Cacao Fruit
- `dried_beans` - Dried Cacao Beans
- `cacao_powder` - Cacao Powder
- `chocolate` - Chocolate Products
- `cacao_butter` - Cacao Butter
- `cacao_nibs` - Cacao Nibs

### Order Status
- `pending` - Order placed, awaiting confirmation
- `confirmed` - Order approved, being prepared
- `processing` - Order being packed
- `shipped` - Order dispatched for delivery
- `delivered` - Order successfully received
- `cancelled` - Order cancelled by user/admin

### Payment Methods
- `cod` - Cash on Delivery
- `gcash` - GCash Mobile Wallet
- `bank_transfer` - Direct Bank Deposit

### Scan Types
- `disease` - Disease detection scan
- `pest` - Pest detection scan

### Disease Classes (5 Classes)
- `Black Pod Rot Disease`
- `Fito Disease` (Phytophthora Root Rot)
- `Monilia Disease`
- `Healthy` (No disease detected)
- `Unknow Data` (Unable to identify)

### Pest Classes (5 Classes)
- `Ant Weaver`
- `Aphids`
- `Mealybug`
- `Healthy` (No pest detected)
- `Unknow Data` (Unable to identify)

### Farm Status
- `active` - Currently operational
- `inactive` - Not in use
- `under_maintenance` - Temporarily closed

### Notification Types
- `info` - Informational message
- `success` - Success confirmation
- `warning` - Warning alert
- `error` - Error notification
- `order_status` - Order status update

---

## Data Relationships

### One-to-Many Relationships

1. **users → orders**
   - One user can have multiple orders
   - Foreign Key: `orders.user_id` → `users.uid`

2. **users → scans**
   - One user can perform multiple scans
   - Foreign Key: `scans.user_id` → `users.uid`

3. **users → farms**
   - One user can own multiple farms
   - Foreign Key: `farms.owner_id` → `users.uid`

4. **users → notifications**
   - One user can have multiple notifications
   - Foreign Key: `notifications.user_id` → `users.uid`

5. **products → order items**
   - One product can be in multiple orders
   - Foreign Key: `orders.items[].product_id` → `products.id`

6. **farms → scans**
   - One farm can have multiple scans
   - Foreign Key: `scans.farm_id` → `farms.id`

### Reference Diagram
```
users (1) ──< (M) orders
users (1) ──< (M) scans
users (1) ──< (M) farms
users (1) ──< (M) notifications
products (1) ──< (M) orders.items
farms (1) ──< (M) scans
```

---

## Data Validation Rules

### Field Constraints

1. **Email Format**: Must match regex `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
2. **Phone Number**: Philippine format `+639XXXXXXXXX` (11 digits after +63)
3. **Price/Amount**: Must be positive number, max 2 decimal places
4. **Confidence Score**: Float between 0.0 and 1.0
5. **Coordinates**:
   - Latitude: -90 to 90
   - Longitude: -180 to 180
6. **Stock Quantity**: Non-negative integer
7. **Image URLs**: Must start with `https://res.cloudinary.com/driikw8gl/`

### Required Field Validation

**Users Collection:**
- `uid`, `email`, `name`, `role`, `created_at`, `is_active`, `email_verified`

**Products Collection:**
- `name`, `category`, `product_type`, `price`, `stock`, `description`, `images`, `is_active`, `created_at`, `updated_at`

**Orders Collection:**
- `order_id`, `user_id`, `user_email`, `user_name`, `items`, `subtotal`, `shipping_cost`, `total_amount`, `status`, `payment_method`, `shipping_address`, `phone_number`, `created_at`, `updated_at`

**Scans Collection:**
- `scan_id`, `user_id`, `user_email`, `user_name`, `user_type`, `type`, `image_url`, `image_hash`, `result`, `confidence`, `recommendations`, `timestamp`

**Farms Collection:**
- `name`, `municipality`, `barangay`, `area`, `trees`, `status`, `lat`, `lng`, `created_at`, `updated_at`

**Notifications Collection:**
- `user_id`, `title`, `message`, `type`, `read`, `created_at`

---

## Security Rules

### Firestore Security Rules (Conceptual)

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Users collection - only owner or admin can read/write
    match /users/{userId} {
      allow read: if request.auth.uid == userId || get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
      allow write: if request.auth.uid == userId || get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
    }
    
    // Products collection - all can read, only admin can write
    match /products/{productId} {
      allow read: if true;
      allow write: if get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
    }
    
    // Orders collection - only order owner or admin can access
    match /orders/{orderId} {
      allow read: if request.auth.uid == resource.data.user_id || get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
      allow create: if request.auth.uid == request.resource.data.user_id;
      allow update: if get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
    }
    
    // Scans collection - only scan owner or admin can access
    match /scans/{scanId} {
      allow read: if request.auth.uid == resource.data.user_id || get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
      allow create: if request.auth.uid == request.resource.data.user_id;
      allow delete: if request.auth.uid == resource.data.user_id;
    }
    
    // Farms collection - all can read, only owner/admin can write
    match /farms/{farmId} {
      allow read: if true;
      allow create: if request.auth != null;
      allow update, delete: if request.auth.uid == resource.data.owner_id || get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
    }
    
    // Notifications collection - only notification owner can access
    match /notifications/{notifId} {
      allow read, update: if request.auth.uid == resource.data.user_id;
      allow create: if get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
    }
  }
}
```

---

## Query Examples

### Common Queries

**1. Get all products in a category:**
```python
products = db.collection('products').where('category', '==', 'dried_beans').where('is_active', '==', True).stream()
```

**2. Get user's recent orders:**
```python
orders = db.collection('orders').where('user_id', '==', user_id).order_by('created_at', direction=firestore.Query.DESCENDING).limit(10).stream()
```

**3. Get disease scans for a farm:**
```python
scans = db.collection('scans').where('farm_id', '==', farm_id).where('type', '==', 'disease').order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
```

**4. Get pending orders:**
```python
orders = db.collection('orders').where('status', '==', 'pending').order_by('created_at').stream()
```

**5. Get unread notifications:**
```python
notifications = db.collection('notifications').where('user_id', '==', user_id).where('read', '==', False).order_by('created_at', direction=firestore.Query.DESCENDING).stream()
```

**6. Get active farms in municipality:**
```python
farms = db.collection('farms').where('municipality', '==', 'Victoria').where('status', '==', 'active').stream()
```

---

## Data Migration Notes

### Image Storage Migration
- **Old**: Local `/media/` directory (ephemeral on Render)
- **New**: Cloudinary CDN (`https://res.cloudinary.com/driikw8gl/`)
- **Status**: Fully migrated as of December 2025

### Farm Data Migration
- **Old**: In-memory `SAMPLE_FARMS` list in views.py
- **New**: Firestore `farms` collection
- **Date**: November 2025
- **Records**: 12 real farms in Oriental Mindoro

### Authentication System
- **Current**: Firebase Authentication + Firestore
- **Session Management**: Django sessions with Firebase tokens
- **Password Reset**: Firebase Auth Email service

---

## Backup & Disaster Recovery

### Backup Strategy
- **Automatic Backups**: Daily Firestore exports to Google Cloud Storage
- **Retention Period**: 30 days
- **Backup Location**: `gs://cacaoguard-backups/firestore/`
- **Image Backups**: Cloudinary automatic backups enabled

### Recovery Procedures
1. **Database Restore**: Use Firebase Console > Firestore > Import/Export
2. **Point-in-Time Recovery**: Available for last 7 days
3. **Image Recovery**: Cloudinary trash retention for 30 days

---

## Performance Optimization

### Implemented Optimizations
1. **Caching**: 5-minute cache for frequently accessed data (`get_cached_firestore_data()`)
2. **Composite Indexes**: Created for common query patterns
3. **Pagination**: Limit queries to 100 documents per request
4. **Image Optimization**: Cloudinary auto-optimization and CDN
5. **Lazy Loading**: Products and scans load on demand

### Query Performance
- **Average Read Time**: 50-150ms
- **Average Write Time**: 100-300ms
- **Index Lookup**: < 10ms
- **Image Load Time**: 200-500ms (CDN)

---

## API Endpoints Using Database

| Endpoint | Method | Collection(s) | Description |
|----------|--------|---------------|-------------|
| `/api/products/` | GET | products | List all active products |
| `/api/products/<id>/` | GET | products | Get product details |
| `/api/farm-data/` | GET, POST, PUT, DELETE | farms | CRUD operations for farms |
| `/api/farm-image/upload/` | POST | - | Upload farm image to Cloudinary |
| `/scan-image/` | POST | scans | Perform disease/pest scan |
| `/api/orders/` | GET, POST | orders, products | Create and list orders |
| `/api/notifications/` | GET | notifications | Get user notifications |
| `/api/scan-history/` | GET | scans | Get user's scan history |

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-11-15 | 1.0 | Initial database design | Development Team |
| 2025-11-20 | 1.1 | Added notifications collection | Development Team |
| 2025-11-25 | 1.2 | Migrated to Cloudinary for images | Development Team |
| 2025-12-01 | 1.3 | Added 12 real farms to farms collection | Development Team |
| 2025-12-05 | 1.4 | Enhanced order tracking fields | Development Team |
| 2025-12-08 | 1.5 | Updated data dictionary documentation | Development Team |

---

**Document Version**: 1.5  
**Last Updated**: December 8, 2025  
**Maintained By**: CacaoGuard Development Team  
**Contact**: jardinesjohnlloyd@gmail.com
