# CacaoGuard System Documentation
## Complete System Analysis and Design Document

---

# TABLE OF CONTENTS

1. [System Overview](#1-system-overview)
2. [User Roles and Responsibilities](#2-user-roles-and-responsibilities)
3. [Functional Requirements](#3-functional-requirements)
4. [Software Specifications](#4-software-specifications)
5. [Use Case Diagram](#5-use-case-diagram)
6. [Activity Diagrams](#6-activity-diagrams)
7. [Context Diagram](#7-context-diagram)
8. [Data Flow Diagram Level 0](#8-data-flow-diagram-level-0)
9. [Database Schema](#9-database-schema)
10. [System Architecture](#10-system-architecture)

---

# 1. SYSTEM OVERVIEW

## 1.1 System Name
**CacaoGuard: AI-Powered Cacao Disease and Pest Detection with E-Commerce Integration**

## 1.2 Purpose
CacaoGuard is a web-based platform designed to help cacao farmers detect diseases and pests in their crops using artificial intelligence, while also providing an integrated marketplace for buying and selling cacao products.

## 1.3 Key Features
- AI-powered disease and pest detection
- Farm mapping and management
- E-commerce marketplace for cacao products
- Order management system
- User dashboard with analytics
- Role-based access control (Admin, Farmer, Guest)

## 1.4 Technology Stack
- **Frontend:** HTML5, CSS3, JavaScript, TailwindCSS
- **Backend:** Python Django 5.1
- **Database:** Firebase Firestore (NoSQL)
- **Storage:** Cloudinary CDN
- **Authentication:** Firebase Authentication
- **Hosting:** Render Cloud Platform

---

# 2. USER ROLES AND RESPONSIBILITIES

## 2.1 ADMIN (Administrator)

### Role Description
System administrator with full control over the platform, responsible for managing products, orders, users, and monitoring system activities.

### Responsibilities
- Manage product inventory (add, edit, delete products)
- Process and fulfill customer orders
- Monitor sales and analytics
- Manage user accounts
- View scan history and statistics
- Configure system settings
- Access all administrative features

### Key Capabilities
- Full CRUD operations on products
- Order status management (pending → confirmed → shipped → delivered)
- View all scans performed by users
- Access to analytics dashboard
- User management
- Farm location management

---

## 2.2 USER (Farmer/Registered User)

### Role Description
Registered farmers or cacao enthusiasts who use the platform for disease detection and purchasing cacao products.

### Responsibilities
- Upload cacao leaf/fruit images for analysis
- View scan results and recommendations
- Browse and purchase products from marketplace
- Manage their orders
- Update profile information
- Track farm locations

### Key Capabilities
- **Unlimited scans** (no daily limit)
- Access to complete scan history
- Shopping cart and checkout functionality
- Order tracking
- Profile management
- Farm mapping features
- Save favorite products

---

## 2.3 GUEST (Visitor)

### Role Description
Unregistered visitors who can explore the platform with limited features before deciding to register.

### Responsibilities
- Explore marketplace products (view only)
- Try disease detection feature (limited)
- View system information
- Register for full access

### Key Capabilities
- **5 scans per day limit**
- View marketplace products (cannot purchase)
- Basic disease detection
- View product details
- Access to registration page

### Limitations
- Cannot purchase products
- Cannot save scan history
- Limited scan attempts
- No order tracking
- No profile features

---

# 3. FUNCTIONAL REQUIREMENTS

## 3.1 Authentication & Authorization

### FR-AUTH-001: User Registration
**Description:** System shall allow new users to register with email and password.
**Actors:** Guest
**Preconditions:** User must have valid email
**Postconditions:** User account created, email verification sent
**Priority:** High

### FR-AUTH-002: User Login
**Description:** System shall authenticate users using Firebase Authentication.
**Actors:** Admin, User, Guest
**Preconditions:** User must have registered account
**Postconditions:** User redirected to role-specific dashboard
**Priority:** High

### FR-AUTH-003: Role-Based Access Control
**Description:** System shall restrict access to features based on user role.
**Actors:** All
**Preconditions:** User authenticated
**Postconditions:** User can only access authorized features
**Priority:** Critical

---

## 3.2 Disease & Pest Detection

### FR-SCAN-001: Image Upload
**Description:** System shall accept image uploads of cacao leaves/fruits.
**Actors:** User, Guest
**Preconditions:** Valid image file (JPG, PNG)
**Postconditions:** Image processed and stored
**Priority:** Critical

### FR-SCAN-002: AI Analysis
**Description:** System shall analyze images using AI models to detect diseases/pests.
**Actors:** System
**Preconditions:** Image uploaded successfully
**Postconditions:** Disease/pest identified with confidence score
**Priority:** Critical

### FR-SCAN-003: Results Display
**Description:** System shall display analysis results with recommendations.
**Actors:** User, Guest
**Preconditions:** Analysis completed
**Postconditions:** Results shown with treatment suggestions
**Priority:** High

### FR-SCAN-004: Scan History
**Description:** System shall maintain history of all scans for registered users.
**Actors:** User
**Preconditions:** User logged in
**Postconditions:** Scan history accessible from dashboard
**Priority:** Medium

### FR-SCAN-005: Guest Scan Limit
**Description:** System shall limit guests to 5 scans per day.
**Actors:** Guest
**Preconditions:** Guest accessing scan feature
**Postconditions:** Scan count tracked, limit enforced
**Priority:** Medium

---

## 3.3 E-Commerce/Marketplace

### FR-SHOP-001: Product Browsing
**Description:** System shall display all active products in marketplace.
**Actors:** Admin, User, Guest
**Preconditions:** Products exist in database
**Postconditions:** Products displayed with images, prices, descriptions
**Priority:** High

### FR-SHOP-002: Product Search & Filter
**Description:** System shall allow users to search and filter products.
**Actors:** User, Guest
**Preconditions:** Multiple products available
**Postconditions:** Filtered results displayed
**Priority:** Medium

### FR-SHOP-003: Shopping Cart
**Description:** System shall allow users to add products to cart.
**Actors:** User
**Preconditions:** User logged in
**Postconditions:** Cart items stored in session
**Priority:** High

### FR-SHOP-004: Checkout Process
**Description:** System shall process orders with shipping and payment details.
**Actors:** User
**Preconditions:** Cart not empty, user logged in
**Postconditions:** Order created, confirmation sent
**Priority:** Critical

### FR-SHOP-005: Payment Methods
**Description:** System shall support multiple payment methods (COD, GCash).
**Actors:** User
**Preconditions:** Checkout initiated
**Postconditions:** Payment method recorded, instructions shown
**Priority:** High

### FR-SHOP-006: Order Tracking
**Description:** System shall allow users to track order status.
**Actors:** User
**Preconditions:** Order placed
**Postconditions:** Status visible (pending, confirmed, shipped, delivered)
**Priority:** High

---

## 3.4 Product Management (Admin)

### FR-PROD-001: Add Product
**Description:** Admin shall be able to add new products with details and images.
**Actors:** Admin
**Preconditions:** Admin logged in
**Postconditions:** Product created, available in marketplace
**Priority:** High

### FR-PROD-002: Edit Product
**Description:** Admin shall be able to modify product details.
**Actors:** Admin
**Preconditions:** Product exists
**Postconditions:** Product updated
**Priority:** Medium

### FR-PROD-003: Delete Product
**Description:** Admin shall be able to remove products from marketplace.
**Actors:** Admin
**Preconditions:** Product exists
**Postconditions:** Product soft-deleted, images removed
**Priority:** Medium

### FR-PROD-004: Stock Management
**Description:** Admin shall be able to manage product inventory levels.
**Actors:** Admin
**Preconditions:** Product exists
**Postconditions:** Stock quantity updated
**Priority:** High

---

## 3.5 Order Management (Admin)

### FR-ORDER-001: View Orders
**Description:** Admin shall view all customer orders.
**Actors:** Admin
**Preconditions:** Orders exist
**Postconditions:** Orders displayed with details
**Priority:** High

### FR-ORDER-002: Update Order Status
**Description:** Admin shall be able to change order status.
**Actors:** Admin
**Preconditions:** Order exists
**Postconditions:** Status updated, user notified
**Priority:** Critical

### FR-ORDER-003: Order Details
**Description:** Admin shall view complete order information.
**Actors:** Admin
**Preconditions:** Order exists
**Postconditions:** Full order details displayed
**Priority:** Medium

### FR-ORDER-004: Print Order
**Description:** Admin shall be able to print order receipts.
**Actors:** Admin
**Preconditions:** Order exists
**Postconditions:** Printable receipt generated
**Priority:** Low

---

## 3.6 Farm Mapping

### FR-FARM-001: Add Farm Location
**Description:** Users shall be able to mark farm locations on map.
**Actors:** User
**Preconditions:** User logged in
**Postconditions:** Farm location saved with coordinates
**Priority:** Medium

### FR-FARM-002: View Farm Map
**Description:** System shall display all farm locations on interactive map.
**Actors:** Admin, User, Guest
**Preconditions:** Farm locations exist
**Postconditions:** Map displayed with markers
**Priority:** Medium

### FR-FARM-003: Farm Statistics
**Description:** System shall show statistics per farm location.
**Actors:** Admin, User
**Preconditions:** Scan data associated with farms
**Postconditions:** Statistics displayed
**Priority:** Low

---

## 3.7 Dashboard & Analytics

### FR-DASH-001: User Dashboard
**Description:** Users shall see personalized dashboard with scan history and orders.
**Actors:** User
**Preconditions:** User logged in
**Postconditions:** Dashboard displayed
**Priority:** High

### FR-DASH-002: Admin Dashboard
**Description:** Admin shall see analytics including sales, orders, scans.
**Actors:** Admin
**Preconditions:** Admin logged in
**Postconditions:** Analytics dashboard displayed
**Priority:** High

### FR-DASH-003: Charts & Graphs
**Description:** System shall display visual analytics using charts.
**Actors:** Admin, User
**Preconditions:** Data available
**Postconditions:** Charts rendered
**Priority:** Medium

---

# 4. SOFTWARE SPECIFICATIONS

## 4.1 Hardware Requirements

### Server Requirements (Render Free Tier)
- **CPU:** 0.1 CPU cores (shared)
- **RAM:** 512 MB
- **Storage:** 512 MB (ephemeral)
- **Bandwidth:** Unlimited

### Client Requirements (End Users)
- **Desktop:**
  - Processor: Intel Core i3 or equivalent
  - RAM: 4 GB minimum
  - Browser: Chrome 90+, Firefox 88+, Edge 90+
  
- **Mobile:**
  - OS: Android 8.0+ or iOS 12+
  - RAM: 2 GB minimum
  - Browser: Chrome Mobile, Safari Mobile

---

## 4.2 Software Requirements

### Development Environment
- **Python:** 3.11.0
- **Django:** 5.1
- **Node.js:** 16+ (for frontend build tools)
- **Git:** Latest version
- **VS Code:** Recommended IDE

### Backend Dependencies
```
Django==5.1
firebase-admin==6.2.0
cloudinary==1.41.0
gunicorn==20.1.0
python-dotenv==1.0.0
Pillow==10.0.0
pytz==2023.3
```

### Frontend Technologies
- HTML5
- CSS3 with TailwindCSS 3.x
- JavaScript (ES6+)
- Alpine.js 3.x
- Chart.js 4.x

### External Services
- **Firebase:**
  - Firestore Database
  - Firebase Authentication
  - Firebase Storage

- **Cloudinary:**
  - Image CDN
  - Image optimization
  - Cloud storage

### Deployment Platform
- **Render:** Web service hosting
- **GitHub:** Version control and CI/CD

---

## 4.3 Database Requirements

### Firebase Firestore Collections

**1. users**
- Document structure: Key-value pairs
- Fields: uid, email, name, role, phone, address
- Indexing: uid (primary key)

**2. products**
- Document structure: Product data
- Fields: id, name, description, price, stock_quantity, images[], is_active, featured
- Indexing: is_active, featured

**3. orders**
- Document structure: Order information
- Fields: order_id, firebase_uid, customer_email, items[], total_amount, status, payment_method, payment_status
- Indexing: firebase_uid, order_id, status

**4. scans**
- Document structure: Scan analysis results
- Fields: scan_id, user_id, image_url, disease_type, pest_type, confidence, recommendations, created_at
- Indexing: user_id, created_at

**5. farm_locations**
- Document structure: Farm geo data
- Fields: location_id, user_id, name, latitude, longitude, area_size, created_at
- Indexing: user_id

---

## 4.4 Security Requirements

### SEC-001: Authentication
- Firebase Authentication with email/password
- JWT token-based session management
- Session timeout: 24 hours

### SEC-002: Authorization
- Role-based middleware protection
- URL-level access control
- Template-level permission checks

### SEC-003: Data Security
- HTTPS only (TLS 1.2+)
- Firebase security rules
- CSRF protection enabled
- XSS prevention

### SEC-004: File Upload Security
- File type validation (images only)
- File size limit: 10 MB
- Virus scanning (via Cloudinary)
- Secure filename sanitization

---

## 4.5 Performance Requirements

### PERF-001: Response Time
- Page load: < 3 seconds
- API response: < 1 second
- Image upload: < 5 seconds
- Scan analysis: < 10 seconds

### PERF-002: Scalability
- Support 100 concurrent users (free tier)
- Handle 1000 scans per day
- Process 100 orders per day

### PERF-003: Availability
- Uptime: 99% (free tier)
- Automatic restart on failure
- Health check monitoring

---

## 4.6 Compatibility Requirements

### Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (latest versions)

### Device Support
- Desktop (Windows, Mac, Linux)
- Tablets (iPad, Android tablets)
- Smartphones (iOS, Android)

### Screen Resolutions
- Minimum: 360x640 (mobile)
- Recommended: 1920x1080 (desktop)
- Responsive design for all sizes

---

# 5. USE CASE DIAGRAM

## Use Case Diagram Description

```
┌─────────────────────────────────────────────────────────────────┐
│                      CacaoGuard System                          │
│                                                                 │
│  ┌──────────┐                                                  │
│  │  GUEST   │───────── View Marketplace                        │
│  └──────────┘    │                                            │
│       │          └─────── Try Scan (5/day limit)              │
│       │                                                        │
│       └───────────────── Register Account                      │
│                                                                │
│  ┌──────────┐                                                 │
│  │   USER   │───────── Login/Logout                           │
│  │ (Farmer) │    │                                           │
│  └──────────┘    ├───── Unlimited Image Scanning             │
│       │          │                                            │
│       │          ├───── View Scan History                     │
│       │          │                                            │
│       │          ├───── Browse Products                       │
│       │          │                                            │
│       │          ├───── Add to Cart                           │
│       │          │                                            │
│       │          ├───── Checkout & Place Order                │
│       │          │                                            │
│       │          ├───── Track Orders                          │
│       │          │                                            │
│       │          ├───── View User Dashboard                   │
│       │          │                                            │
│       │          └───── Manage Farm Locations                 │
│                                                                │
│  ┌──────────┐                                                 │
│  │  ADMIN   │───────── Manage Products (CRUD)                 │
│  └──────────┘    │                                           │
│                  ├───── Process Orders                        │
│                  │                                            │
│                  ├───── Update Order Status                   │
│                  │                                            │
│                  ├───── View All Scans                        │
│                  │                                            │
│                  ├───── View Sales Analytics                  │
│                  │                                            │
│                  ├───── Manage Users                          │
│                  │                                            │
│                  └───── View Admin Dashboard                  │
│                                                                │
│  ┌───────────────┐                                           │
│  │  AI SYSTEM    │──── Analyze Images                        │
│  │  (Internal)   │     │                                     │
│  └───────────────┘     └──── Generate Recommendations        │
│                                                                │
└─────────────────────────────────────────────────────────────────┘

External Systems:
┌─────────────────┐
│    Firebase     │──── Authentication
│   (Database)    │──── Data Storage
└─────────────────┘

┌─────────────────┐
│   Cloudinary    │──── Image Storage
│   (CDN)         │──── Image Optimization
└─────────────────┘

┌─────────────────┐
│     GCash       │──── Payment Processing
│  (Payment API)  │     (Manual Verification)
└─────────────────┘
```

---

# 6. ACTIVITY DIAGRAMS

## 6.1 Activity Diagram: User Registration Process

```
START
  │
  ▼
[User clicks "Sign Up"]
  │
  ▼
[Enter Email, Password, Name]
  │
  ▼
<Valid Input?> ──No──> [Show Error Message] ──┐
  │ Yes                                        │
  ▼                                            │
[Submit to Firebase Auth]                      │
  │                                            │
  ▼                                            │
<Registration Success?> ──No─────────────────┘
  │ Yes
  ▼
[Create User Document in Firestore]
  │
  ▼
[Send Verification Email]
  │
  ▼
[Redirect to Dashboard]
  │
  ▼
END
```

---

## 6.2 Activity Diagram: Disease Detection Scan

```
START
  │
  ▼
[User/Guest clicks "Scan"]
  │
  ▼
<Is User?> ──No──> <Guest Scan Limit Reached?> ──Yes──> [Show "Register for Unlimited Scans"] ──> END
  │ Yes              │ No
  │                  │
  └─────────────────┘
  │
  ▼
[User Uploads Image]
  │
  ▼
<Valid Image File?> ──No──> [Show Error: Invalid File] ──> END
  │ Yes
  ▼
[Upload to Cloudinary]
  │
  ▼
[AI Model Analyzes Image]
  │
  ▼
<Disease/Pest Detected?>
  │ Yes              │ No
  ▼                  ▼
[Get Disease Info]  [Return "Healthy"]
  │                  │
  ▼                  │
[Generate          │
 Recommendations]   │
  │                  │
  └──────┬──────────┘
         ▼
[Save Scan to Database]
  │
  ▼
[Display Results to User]
  │
  ▼
<Is Registered User?> ──Yes──> [Save to Scan History]
  │ No                           │
  ▼                              │
[Increment Guest Scan Count]   │
  │                              │
  └──────────────────────────────┘
  │
  ▼
END
```

---

## 6.3 Activity Diagram: E-Commerce Checkout Process

```
START
  │
  ▼
[User browses Marketplace]
  │
  ▼
[Click "Add to Cart"]
  │
  ▼
<User Logged In?> ──No──> [Redirect to Login] ──> [After Login] ──┐
  │ Yes                                                            │
  └────────────────────────────────────────────────────────────────┘
  │
  ▼
[Add Product to Session Cart]
  │
  ▼
<Continue Shopping?> ──Yes──> [Browse More Products] ──┐
  │ No                                                  │
  ▼                                                     │
[Click "Checkout"]                                      │
  │                                                     │
  ▼                                                     │
[Fill Shipping Information]                             │
  │                                                     │
  ▼                                                     │
[Select Payment Method]                                 │
  │                                                     │
  ├──[COD]──> [Show COD Instructions]                  │
  │           │                                         │
  └──[GCash]──> [Show GCash Payment Details]           │
                │                                       │
                ▼                                       │
[Click "Place Order"]                                   │
  │                                                     │
  ▼                                                     │
<All Fields Valid?> ──No──> [Show Validation Error] ──┘
  │ Yes
  ▼
[Generate Unique Order ID]
  │
  ▼
[Save Order to Firestore]
  │
  ▼
[Clear Shopping Cart]
  │
  ▼
[Redirect to Order Confirmation]
  │
  ▼
<Payment Method is GCash?> ──Yes──> [Display GCash Instructions]
  │ No                                │
  ▼                                   ▼
[Display COD Instructions]    [Show: Account, Amount, Reference]
  │                                   │
  └───────────────┬───────────────────┘
                  ▼
[Show Order Summary]
  │
  ▼
END
```

---

## 6.4 Activity Diagram: Admin Order Management

```
START
  │
  ▼
[Admin Login]
  │
  ▼
[Navigate to Orders Page]
  │
  ▼
[System fetches all orders from Firestore]
  │
  ▼
[Display Orders List with Filters]
  │
  ▼
[Admin selects an Order]
  │
  ▼
[Display Order Details]
  │  (Customer Info, Items, Total, Status)
  ▼
<Admin Action?>
  │
  ├──[Update Status]──> [Select New Status] ──> [Save to Firestore] ──┐
  │                     (Pending → Confirmed → Shipped → Delivered)    │
  │                                                                    │
  ├──[Print Order]────> [Generate Print View] ──> [Print Receipt] ────┤
  │                                                                    │
  ├──[View Customer]──> [Show Customer Profile] ─────────────────────┤
  │                                                                    │
  └──[Cancel Order]───> <Confirm Cancel?> ──Yes──> [Update Status] ──┤
                         │ No                                         │
                         └────────────────────────────────────────────┘
                                                                      │
                                                                      ▼
                                              [Refresh Orders List]
                                                                      │
                                                                      ▼
                                              <Continue Managing?> ──Yes──┐
                                                │ No                      │
                                                ▼                         │
                                              END <────────────────────────┘
```

---

# 7. CONTEXT DIAGRAM

## Context Diagram: CacaoGuard System

```
                        ┌─────────────────────────────────────┐
                        │                                     │
    ┌──────────┐        │                                     │        ┌────────────────┐
    │  GUEST   │───────>│        CacaoGuard System            │<───────│     ADMIN      │
    │ (Visitor)│<───────│    (Web Application)                │───────>│ (Administrator)│
    └──────────┘        │                                     │        └────────────────┘
         │              │  Core Functions:                    │               │
         │              │  - Disease Detection                │               │
         │              │  - E-Commerce                       │               │
    View Products       │  - Order Management                 │          Manage Products
    Limited Scans       │  - Farm Mapping                     │          Process Orders
    Register            │  - User Management                  │          View Analytics
                        │                                     │          Manage Users
                        │                                     │
    ┌──────────┐        │                                     │
    │   USER   │───────>│                                     │
    │ (Farmer) │<───────│                                     │
    └──────────┘        │                                     │
         │              └─────────────────────────────────────┘
         │                        │      │      │
    Scan Images                   │      │      │
    Purchase Products             │      │      │
    Track Orders                  │      │      │
    Manage Profile                ▼      ▼      ▼
                            
                    ┌─────────────┐  ┌──────────────┐  ┌─────────────┐
                    │   Firebase  │  │  Cloudinary  │  │    GCash    │
                    │  Firestore  │  │     CDN      │  │  (Payment)  │
                    │             │  │              │  │             │
                    │ - Auth      │  │ - Image      │  │ - Payment   │
                    │ - Database  │  │   Storage    │  │   Processing│
                    │ - Storage   │  │ - Image CDN  │  │ - Verification│
                    └─────────────┘  └──────────────┘  └─────────────┘

External Entities:
- GUEST: Unregistered visitors exploring the system
- USER: Registered farmers using scan and shopping features
- ADMIN: System administrators managing content and orders
- Firebase: Backend services for authentication and data storage
- Cloudinary: Image hosting and CDN service
- GCash: Payment processing service (manual verification)
```

---

# 8. DATA FLOW DIAGRAM LEVEL 0

## DFD Level 0: CacaoGuard System

```
┌────────────────────────────────────────────────────────────────────────┐
│                       Level 0: CacaoGuard System                       │
└────────────────────────────────────────────────────────────────────────┘

    GUEST                        USER (Farmer)                    ADMIN
      │                              │                              │
      │ Image for Scan              │ Image for Scan              │
      │─────────────────────────────│─────────────────────────────│
      │                             │                             │
      │ Registration Data           │ Login Credentials           │ Login Credentials
      │────────────────────┐        │────────────────┐            │────────────┐
      │                    │        │                │            │            │
      │                    ▼        ▼                ▼            ▼            │
      │               ┌────────────────────────────────────────────────┐      │
      │               │                                                │      │
      │               │           1.0 AUTHENTICATION                   │      │
      │               │         Manage User Sessions                   │      │
      │               │                                                │      │
      │               └─────────────────┬──────────────────────────────┘      │
      │                                 │                                     │
      │                         User Token/Session                            │
      │                                 │                                     │
      │                 ┌───────────────┴────────────────┐                   │
      │                 │                                │                   │
      │                 ▼                                ▼                   │
      │       ┌──────────────────────┐        ┌──────────────────────┐      │
      │       │                      │        │                      │      │
      │       │  2.0 DISEASE/PEST    │        │   3.0 E-COMMERCE     │      │
      │<──────│     DETECTION        │        │     MANAGEMENT       │──────│
      │       │  AI Image Analysis   │        │  Products & Orders   │      │
      │       │                      │        │                      │      │
      │       └──────────┬───────────┘        └───────────┬──────────┘      │
      │                  │                                │                  │
      │        Scan Results                     Product Data                │
      │                  │                                │                  │
      │                  │                    Order Info  │                  │
      │                  │                                │                  │
      │                  ▼                                ▼                  │
      │       ┌──────────────────────┐        ┌──────────────────────┐      │
      │       │                      │        │                      │      │
      │       │   4.0 DASHBOARD      │        │  5.0 ORDER          │      │
      │<──────│   & ANALYTICS        │        │     PROCESSING       │──────│
      │       │  User/Admin Views    │        │  Status & Payment   │      │
      │       │                      │        │                      │      │
      │       └──────────┬───────────┘        └───────────┬──────────┘      │
      │                  │                                │                  │
      │                  │                                │                  │
      │                  └────────────┬───────────────────┘                  │
      │                               │                                      │
      │                               ▼                                      │
      │                    ┌────────────────────┐                           │
      │                    │                    │                           │
      │                    │  6.0 DATA STORE    │                           │
      │                    │   Firebase         │                           │
      │                    │   Cloudinary       │                           │
      │                    │                    │                           │
      │                    └────────────────────┘                           │
      │                                                                      │
      └──────────────────────────────────────────────────────────────────────┘

Data Stores:
D1: Firebase Authentication (User credentials)
D2: Firebase Firestore (Users, Products, Orders, Scans)
D3: Cloudinary (Product images, Scan images)
D4: Session Storage (Shopping cart, temporary data)

Data Flows:
- Guest/User → Image → Detection System → Results → User
- User → Order Data → Order Processing → Confirmation → User
- Admin → Product Data → E-Commerce System → Products → Users
- All Processes ↔ Data Stores (Read/Write operations)
```

---

# 9. DATABASE SCHEMA

## 9.1 Firebase Firestore Collections

### Collection: `users`
**Purpose:** Store user account information

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| uid | String | Firebase unique ID (Primary Key) | Required, Unique |
| email | String | User email address | Required, Unique, Valid email |
| name | String | Full name | Required |
| role | String | User role (admin/user/guest) | Required, Enum |
| phone | String | Contact number | Optional |
| address | String | Physical address | Optional |
| profile_image | String | URL to profile picture | Optional |
| created_at | Timestamp | Account creation date | Auto-generated |
| last_login | Timestamp | Last login timestamp | Auto-updated |
| is_active | Boolean | Account status | Default: true |

**Indexes:**
- uid (Primary)
- email
- role

---

### Collection: `products`
**Purpose:** Store marketplace product information

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | String | Product ID (Primary Key) | Auto-generated |
| name | String | Product name | Required, Max 200 chars |
| description | String | Product description | Required |
| price | Number | Product price (₱) | Required, Min: 0 |
| stock_quantity | Number | Available stock | Required, Min: 0 |
| images | Array<String> | Array of Cloudinary URLs | Required, Min: 1 image |
| category | String | Product category | Required |
| is_active | Boolean | Visibility status | Default: true |
| featured | Boolean | Featured product flag | Default: false |
| created_at | Timestamp | Creation date | Auto-generated |
| updated_at | Timestamp | Last update | Auto-updated |
| created_by | String | Admin UID who created | Required |

**Indexes:**
- id (Primary)
- is_active
- featured
- category

**Sample Data:**
```json
{
  "id": "VpPjYPOjbM3O2uL9NfsX",
  "name": "Trinitario Cacao Fruit",
  "description": "Premium trinitario cacao variety",
  "price": 350.00,
  "stock_quantity": 50,
  "images": ["https://res.cloudinary.com/driikw8gl/image/upload/..."],
  "category": "Fresh Cacao",
  "is_active": true,
  "featured": false,
  "created_at": "2025-11-01T10:30:00Z",
  "updated_at": "2025-11-07T14:20:00Z"
}
```

---

### Collection: `orders`
**Purpose:** Store customer orders

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| order_id | String | Unique order identifier | Required, Unique, 8 chars |
| firebase_uid | String | Customer UID | Required, Foreign Key |
| customer_first_name | String | First name | Required |
| customer_last_name | String | Last name | Required |
| customer_email | String | Email address | Required, Valid email |
| customer_name | String | Full name | Required |
| phone_number | String | Contact number | Required |
| shipping_address | String | Delivery address | Required |
| status | String | Order status | Required, Enum |
| payment_method | String | Payment type | Required, Enum |
| payment_status | String | Payment status | Required, Enum |
| total_amount | Number | Total price (₱) | Required, Min: 0 |
| items | Array<Object> | Ordered products | Required, Min: 1 |
| notes | String | Customer notes | Optional |
| created_at | Timestamp | Order date | Auto-generated |
| order_date | String | Formatted date | Required |

**Order Status Values:**
- `pending` - Awaiting admin confirmation
- `confirmed` - Order confirmed by admin
- `shipped` - Order dispatched
- `delivered` - Order completed
- `cancelled` - Order cancelled

**Payment Method Values:**
- `cod` - Cash on Delivery
- `gcash` - GCash payment

**Payment Status Values:**
- `pending` - Awaiting payment
- `paid` - Payment received
- `cod` - Cash on delivery (pay on receive)

**Items Structure:**
```json
{
  "product_id": "VpPjYPOjbM3O2uL9NfsX",
  "product_name": "Trinitario Cacao Fruit",
  "quantity": 2,
  "price": 350.00,
  "total_price": 700.00
}
```

**Sample Order:**
```json
{
  "order_id": "DE700B02",
  "firebase_uid": "abc123xyz",
  "customer_first_name": "Juan",
  "customer_last_name": "Dela Cruz",
  "customer_email": "juan@example.com",
  "phone_number": "09171234567",
  "shipping_address": "123 Main St, Manila",
  "status": "pending",
  "payment_method": "gcash",
  "payment_status": "pending",
  "total_amount": 1050.00,
  "items": [
    {
      "product_id": "VpPjYPOjbM3O2uL9NfsX",
      "product_name": "Trinitario Cacao Fruit",
      "quantity": 3,
      "price": 350.00,
      "total_price": 1050.00
    }
  ],
  "created_at": "2025-11-07T15:30:00Z",
  "order_date": "2025-11-07 15:30:00"
}
```

**Indexes:**
- order_id (Primary)
- firebase_uid
- status
- payment_status
- created_at

---

### Collection: `scans`
**Purpose:** Store disease/pest detection scan results

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| scan_id | String | Unique scan ID | Auto-generated |
| user_id | String | User UID (null for guest) | Optional |
| image_url | String | Cloudinary URL of scanned image | Required |
| scan_type | String | disease or pest | Required, Enum |
| result | String | Detected issue name | Required |
| confidence | Number | AI confidence score (0-100) | Required, 0-100 |
| recommendations | String | Treatment suggestions | Required |
| created_at | Timestamp | Scan timestamp | Auto-generated |
| farm_location_id | String | Associated farm (if any) | Optional |

**Sample Scan:**
```json
{
  "scan_id": "scan_2025110701",
  "user_id": "abc123xyz",
  "image_url": "https://res.cloudinary.com/.../leaf_scan.jpg",
  "scan_type": "disease",
  "result": "Black Pod Disease",
  "confidence": 92.5,
  "recommendations": "Apply copper-based fungicide. Remove infected pods immediately. Improve drainage.",
  "created_at": "2025-11-07T16:45:00Z"
}
```

**Indexes:**
- scan_id (Primary)
- user_id
- created_at

---

### Collection: `farm_locations`
**Purpose:** Store farm location data

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| location_id | String | Unique location ID | Auto-generated |
| user_id | String | Farm owner UID | Required, Foreign Key |
| name | String | Farm name | Required |
| latitude | Number | GPS latitude | Required |
| longitude | Number | GPS longitude | Required |
| area_size | Number | Farm area (hectares) | Optional |
| notes | String | Additional info | Optional |
| created_at | Timestamp | Creation date | Auto-generated |

**Sample Farm Location:**
```json
{
  "location_id": "farm_001",
  "user_id": "abc123xyz",
  "name": "Main Farm - Davao",
  "latitude": 7.1907,
  "longitude": 125.4553,
  "area_size": 2.5,
  "notes": "Primary cacao plantation",
  "created_at": "2025-11-01T08:00:00Z"
}
```

**Indexes:**
- location_id (Primary)
- user_id

---

## 9.2 Entity Relationship Diagram

```
┌─────────────────┐              ┌─────────────────┐
│     USERS       │              │    PRODUCTS     │
├─────────────────┤              ├─────────────────┤
│ uid (PK)        │              │ id (PK)         │
│ email           │              │ name            │
│ name            │              │ description     │
│ role            │              │ price           │
│ phone           │              │ stock_quantity  │
│ address         │              │ images[]        │
│ created_at      │              │ category        │
│ is_active       │              │ is_active       │
└────────┬────────┘              │ featured        │
         │                       └────────┬────────┘
         │                                │
         │ 1:N                            │
         │                                │
         ▼                                │
┌─────────────────┐                       │
│     ORDERS      │                       │
├─────────────────┤                       │
│ order_id (PK)   │                       │
│ firebase_uid(FK)│───────────────────────┘ N:M
│ customer_name   │                       (via items[])
│ total_amount    │
│ status          │
│ payment_method  │
│ items[]         │◄──┐
│ created_at      │   │ Contains
└────────┬────────┘   │
         │            │
         │ 1:N        │
         │            │
         ▼            │
┌─────────────────┐   │
│     SCANS       │   │
├─────────────────┤   │
│ scan_id (PK)    │   │
│ user_id (FK)    │───┘
│ image_url       │
│ result          │
│ confidence      │
│ created_at      │
└────────┬────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────┐
│ FARM_LOCATIONS  │
├─────────────────┤
│ location_id(PK) │
│ user_id (FK)    │
│ name            │
│ latitude        │
│ longitude       │
│ area_size       │
└─────────────────┘

Relationships:
- USER (1) ──< (N) ORDERS
- USER (1) ──< (N) SCANS
- USER (1) ──< (N) FARM_LOCATIONS
- PRODUCTS (N) ──< (M) ORDERS (through items array)
```

---

# 10. SYSTEM ARCHITECTURE

## 10.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Desktop    │  │    Tablet    │  │    Mobile    │          │
│  │   Browser    │  │   Browser    │  │   Browser    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
│         └──────────────────┴──────────────────┘                 │
│                            │                                     │
│                            │ HTTPS                               │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                          │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Django Templates (Server-Side)               │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                │ │
│  │  │  Admin   │  │   User   │  │  Guest   │                │ │
│  │  │  Views   │  │  Views   │  │  Views   │                │ │
│  │  └──────────┘  └──────────┘  └──────────┘                │ │
│  │                                                            │ │
│  │  Frontend: HTML5, TailwindCSS, Alpine.js, Chart.js       │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                          │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                 Django 5.1 Framework                       │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │              Middleware Layer                        │ │ │
│  │  │  • Authentication Middleware                         │ │ │
│  │  │  • Role-Based Access Control (RBAC)                 │ │ │
│  │  │  • CSRF Protection                                   │ │ │
│  │  │  • Session Management                                │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │                   Views Layer                        │ │ │
│  │  │  ┌─────────────┐  ┌──────────────┐  ┌────────────┐ │ │ │
│  │  │  │   Auth      │  │   Scan       │  │  Ecommerce │ │ │ │
│  │  │  │   Views     │  │   Views      │  │   Views    │ │ │ │
│  │  │  └─────────────┘  └──────────────┘  └────────────┘ │ │ │
│  │  │  ┌─────────────┐  ┌──────────────┐  ┌────────────┐ │ │ │
│  │  │  │  Admin      │  │   Dashboard  │  │   Farm     │ │ │ │
│  │  │  │   Views     │  │   Views      │  │   Views    │ │ │ │
│  │  │  └─────────────┘  └──────────────┘  └────────────┘ │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │                  Services Layer                      │ │ │
│  │  │  • Firebase Service (Auth, Firestore)               │ │ │
│  │  │  • Cloudinary Service (Image Upload)                │ │ │
│  │  │  • AI Analysis Service (Disease Detection)          │ │ │
│  │  │  • Order Processing Service                         │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │    Firebase      │  │    Cloudinary    │  │   Session    │ │
│  │   Firestore      │  │       CDN        │  │   Storage    │ │
│  │                  │  │                  │  │              │ │
│  │  • users         │  │  • Product       │  │  • Cart      │ │
│  │  • products      │  │    Images        │  │  • Temp Data │ │
│  │  • orders        │  │  • Scan Images   │  │              │ │
│  │  • scans         │  │                  │  └──────────────┘ │
│  │  • farm_loc      │  └──────────────────┘                   │
│  └──────────────────┘                                         │
│                                                                 │
│  ┌──────────────────┐                                          │
│  │    Firebase      │                                          │
│  │ Authentication   │                                          │
│  │                  │                                          │
│  │  • Email/Pass    │                                          │
│  │  • JWT Tokens    │                                          │
│  └──────────────────┘                                          │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT LAYER                             │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Render Platform                         │  │
│  │                                                          │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │         Gunicorn WSGI Server                       │ │  │
│  │  │  (2 workers, 120s timeout)                        │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  │                                                          │  │
│  │  Instance: Free Tier (512MB RAM, 0.1 CPU)              │  │
│  │  Region: Singapore                                      │  │
│  │  Auto-deploy: GitHub production-ready branch           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10.2 Technology Stack Details

### Frontend Technologies
- **HTML5:** Structure
- **TailwindCSS 3.x:** Styling framework
- **JavaScript ES6+:** Interactivity
- **Alpine.js:** Lightweight reactivity
- **Chart.js:** Data visualization

### Backend Technologies
- **Python 3.11:** Programming language
- **Django 5.1:** Web framework
- **Gunicorn:** WSGI server
- **Firebase Admin SDK:** Backend services

### Storage & CDN
- **Firebase Firestore:** NoSQL database
- **Firebase Storage:** File storage
- **Cloudinary:** Image CDN and optimization

### Authentication
- **Firebase Authentication:** User management
- **JWT Tokens:** Session handling

### Deployment
- **Render:** Cloud platform
- **GitHub:** Version control and CI/CD

---

## 10.3 Security Architecture

```
┌────────────────────────────────────────────────┐
│           Security Layers                      │
├────────────────────────────────────────────────┤
│                                                │
│  1. Transport Layer Security (TLS/HTTPS)      │
│     • All communication encrypted             │
│     • SSL certificates                        │
│                                                │
│  2. Authentication Layer                       │
│     • Firebase Authentication                 │
│     • JWT token validation                    │
│     • Session management                      │
│                                                │
│  3. Authorization Layer                        │
│     • Role-based middleware                   │
│     • URL access control                      │
│     • Template permission checks              │
│                                                │
│  4. Application Security                       │
│     • CSRF protection                         │
│     • XSS prevention                          │
│     • SQL injection protection (Firestore)    │
│     • File upload validation                  │
│                                                │
│  5. Data Security                              │
│     • Firebase security rules                 │
│     • Encrypted data transmission             │
│     • Secure password hashing                 │
│                                                │
└────────────────────────────────────────────────┘
```

---

# APPENDIX

## A. Glossary

**AI (Artificial Intelligence):** Technology that simulates human intelligence for tasks like image recognition.

**CDN (Content Delivery Network):** Distributed server network that delivers web content efficiently.

**CRUD:** Create, Read, Update, Delete operations.

**Firestore:** Google's NoSQL cloud database.

**JWT (JSON Web Token):** Secure method for transmitting information between parties.

**RBAC (Role-Based Access Control):** Security paradigm restricting system access based on user roles.

**WSGI (Web Server Gateway Interface):** Python standard for web server and application communication.

---

## B. Acronyms

- **API:** Application Programming Interface
- **CDN:** Content Delivery Network
- **COD:** Cash on Delivery
- **CSRF:** Cross-Site Request Forgery
- **DFD:** Data Flow Diagram
- **HTTPS:** Hypertext Transfer Protocol Secure
- **ML:** Machine Learning
- **NoSQL:** Not Only SQL
- **REST:** Representational State Transfer
- **SQL:** Structured Query Language
- **TLS:** Transport Layer Security
- **UI:** User Interface
- **UX:** User Experience
- **XSS:** Cross-Site Scripting

---

## C. References

1. Django Documentation: https://docs.djangoproject.com/
2. Firebase Documentation: https://firebase.google.com/docs
3. Cloudinary Documentation: https://cloudinary.com/documentation
4. Render Documentation: https://render.com/docs
5. TailwindCSS Documentation: https://tailwindcss.com/docs

---

**Document Version:** 1.0  
**Last Updated:** November 7, 2025  
**Prepared By:** CacaoGuard Development Team  
**Status:** Final

---

END OF DOCUMENT
