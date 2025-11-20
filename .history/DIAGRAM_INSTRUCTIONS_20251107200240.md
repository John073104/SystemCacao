# CacaoGuard System Diagrams
## Instructions for Creating Diagrams in Word/Draw.io

---

## HOW TO CREATE THESE DIAGRAMS

### Method 1: Using Microsoft Word
1. Open Microsoft Word
2. Go to: Insert → SmartArt → Process/Hierarchy
3. Use the text descriptions below to recreate each diagram
4. Format with colors and shapes as described

### Method 2: Using Draw.io (Recommended)
1. Go to: https://app.diagrams.net/
2. Create new diagram
3. Use shapes from left panel
4. Follow layouts below

### Method 3: Using Lucidchart
1. Go to: https://www.lucidchart.com/
2. Use UML/Flowchart templates
3. Drag and drop shapes

---

# DIAGRAM 1: USE CASE DIAGRAM

## Elements to Draw:

### Actors (Stick Figures):
1. **GUEST** (left side, top)
2. **USER/Farmer** (left side, middle)
3. **ADMIN** (left side, bottom)
4. **AI System** (right side - different icon, gear/robot)

### System Boundary (Rectangle):
- Large rectangle containing all use cases
- Label: "CacaoGuard System"

### Use Cases (Ovals inside rectangle):

**Guest Use Cases:**
- View Marketplace
- Try Scan (5/day limit)
- Register Account

**User Use Cases:**
- Login/Logout
- Unlimited Image Scanning
- View Scan History
- Browse Products
- Add to Cart
- Checkout & Place Order
- Track Orders
- View User Dashboard
- Manage Farm Locations

**Admin Use Cases:**
- Manage Products (CRUD)
- Process Orders
- Update Order Status
- View All Scans
- View Sales Analytics
- Manage Users
- View Admin Dashboard

**AI System Use Cases:**
- Analyze Images
- Generate Recommendations

### Relationships (Lines):
- Connect actors to their use cases with solid lines
- Guest can also do: Register Account (points to User actor)
- Use dotted lines for «include» or «extend» relationships

### External Systems (Boxes outside main rectangle):
- Firebase (Database icon)
- Cloudinary (Cloud icon)
- GCash (Payment icon)

---

# DIAGRAM 2: ACTIVITY DIAGRAM - User Registration

## Swimlanes (Columns):
1. User
2. System
3. Firebase

## Steps to Draw:

### User Lane:
1. **START** (filled circle)
2. [Click "Sign Up"] (rounded rectangle)
3. [Enter Email, Password, Name] (rounded rectangle)
4. [Submit Form] (rounded rectangle)

### System Lane:
5. <Valid Input?> (diamond - decision)
   - If NO → [Show Error Message] → back to step 3
   - If YES → continue
6. [Send to Firebase Auth] (rounded rectangle)
7. <Registration Success?> (diamond)
   - If NO → [Show Error] → back to step 3
   - If YES → continue
8. [Create User in Firestore] (rounded rectangle)
9. [Send Verification Email] (rounded rectangle)
10. [Redirect to Dashboard] (rounded rectangle)

### Firebase Lane:
11. [Store User Data] (rounded rectangle)
12. **END** (filled circle with border)

### Arrows:
- Solid arrows show flow
- Label branches (Yes/No)
- Cross swimlane arrows show data transfer

---

# DIAGRAM 3: ACTIVITY DIAGRAM - Disease Detection Scan

## Elements:

**START** → User clicks "Scan"

**Decision 1:** Is User?
- YES → Go to step 3
- NO → Check Guest Limit

**Guest Path:**
- <Guest Scan Limit Reached?>
  - YES → Show "Register for Unlimited" → END
  - NO → Continue to upload

**Main Flow:**
1. [User Uploads Image]
2. <Valid Image File?>
   - NO → [Show Error] → END
   - YES → Continue
3. [Upload to Cloudinary]
4. [AI Model Analyzes Image]
5. <Disease/Pest Detected?>
   - YES → [Get Disease Info] → [Generate Recommendations]
   - NO → [Return "Healthy"]
6. [Save Scan to Database]
7. [Display Results to User]
8. <Is Registered User?>
   - YES → [Save to Scan History]
   - NO → [Increment Guest Counter]
9. **END**

---

# DIAGRAM 4: ACTIVITY DIAGRAM - Checkout Process

## Swimlanes:
1. User
2. System
3. Firestore

## Flow:

1. **START**
2. [Browse Marketplace]
3. [Click "Add to Cart"]
4. <User Logged In?>
   - NO → [Redirect to Login] → (back after login)
   - YES → Continue
5. [Add to Session Cart]
6. <Continue Shopping?>
   - YES → Back to Browse
   - NO → Continue
7. [Click "Checkout"]
8. [Fill Shipping Information]
9. [Select Payment Method]
   - COD → [Show COD Instructions]
   - GCash → [Show GCash Payment Details]
10. [Click "Place Order"]
11. <All Fields Valid?>
    - NO → [Show Validation Error] → Back to step 8
    - YES → Continue
12. [Generate Order ID]
13. [Save Order to Firestore]
14. [Clear Shopping Cart]
15. [Redirect to Confirmation]
16. <Payment Method?>
    - GCash → [Display GCash Instructions with account details]
    - COD → [Display COD Instructions]
17. [Show Order Summary]
18. **END**

---

# DIAGRAM 5: CONTEXT DIAGRAM

## Center: CacaoGuard System (Large rounded rectangle)

### Core Functions (inside):
- Disease Detection
- E-Commerce
- Order Management
- Farm Mapping
- User Management

### External Entities:

**Top Left - GUEST (Stick figure):**
Arrows TO system:
- View Products
- Limited Scans
- Register

Arrows FROM system:
- Product Information
- Scan Results

**Left - USER/Farmer (Stick figure):**
Arrows TO system:
- Scan Images
- Purchase Products
- Track Orders
- Manage Profile

Arrows FROM system:
- Analysis Results
- Order Confirmations
- Dashboard Data

**Top Right - ADMIN (Stick figure):**
Arrows TO system:
- Manage Products
- Process Orders
- View Analytics
- Manage Users

Arrows FROM system:
- Sales Reports
- Order Lists
- System Statistics

**Bottom - External Systems (Boxes):**

1. **Firebase (Database icon)**
   - Auth
   - Database
   - Storage

2. **Cloudinary (Cloud icon)**
   - Image Storage
   - Image CDN

3. **GCash (Payment icon)**
   - Payment Processing
   - Verification

### Arrows:
- Bidirectional between actors and system
- Unidirectional from system to external services

---

# DIAGRAM 6: DATA FLOW DIAGRAM LEVEL 0

## Processes (Circles numbered):

1. **1.0 AUTHENTICATION**
   - Manage User Sessions

2. **2.0 DISEASE/PEST DETECTION**
   - AI Image Analysis

3. **3.0 E-COMMERCE MANAGEMENT**
   - Products & Orders

4. **4.0 DASHBOARD & ANALYTICS**
   - User/Admin Views

5. **5.0 ORDER PROCESSING**
   - Status & Payment

6. **6.0 DATA STORE** (Double horizontal lines)
   - Firebase
   - Cloudinary

## Data Flows (Labeled arrows):

**From GUEST:**
- Image for Scan → Process 2.0
- Registration Data → Process 1.0

**From USER:**
- Image for Scan → Process 2.0
- Login Credentials → Process 1.0
- Order Data → Process 5.0
- Cart Data → Process 3.0

**From ADMIN:**
- Login Credentials → Process 1.0
- Product Data → Process 3.0
- Order Updates → Process 5.0

**Between Processes:**
- 1.0 → User Token/Session → 2.0, 3.0, 4.0, 5.0
- 2.0 → Scan Results → 4.0
- 3.0 → Product Data → 4.0
- 5.0 → Order Info → 4.0
- All processes ↔ 6.0 (Data Store)

**To Actors:**
- Process 2.0 → Scan Results → USER/GUEST
- Process 3.0 → Product Info → ALL
- Process 4.0 → Dashboard → USER/ADMIN
- Process 5.0 → Confirmation → USER

---

# DIAGRAM 7: DATABASE SCHEMA (ERD)

## Tables/Collections (Rectangles):

### 1. USERS
```
┌─────────────────┐
│     USERS       │
├─────────────────┤
│ uid (PK)        │
│ email           │
│ name            │
│ role            │
│ phone           │
│ address         │
│ created_at      │
│ is_active       │
└─────────────────┘
```

### 2. PRODUCTS
```
┌─────────────────┐
│    PRODUCTS     │
├─────────────────┤
│ id (PK)         │
│ name            │
│ description     │
│ price           │
│ stock_quantity  │
│ images[]        │
│ category        │
│ is_active       │
│ featured        │
└─────────────────┘
```

### 3. ORDERS
```
┌─────────────────┐
│     ORDERS      │
├─────────────────┤
│ order_id (PK)   │
│ firebase_uid(FK)│
│ customer_name   │
│ total_amount    │
│ status          │
│ payment_method  │
│ items[]         │
│ created_at      │
└─────────────────┘
```

### 4. SCANS
```
┌─────────────────┐
│     SCANS       │
├─────────────────┤
│ scan_id (PK)    │
│ user_id (FK)    │
│ image_url       │
│ result          │
│ confidence      │
│ created_at      │
└─────────────────┘
```

### 5. FARM_LOCATIONS
```
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
```

## Relationships (Connect with lines):

1. **USERS (1) ──── (N) ORDERS**
   - One user can have many orders
   - Line from USERS.uid to ORDERS.firebase_uid
   - Label: "1:N" or "1..*"

2. **USERS (1) ──── (N) SCANS**
   - One user can have many scans
   - Line from USERS.uid to SCANS.user_id

3. **USERS (1) ──── (N) FARM_LOCATIONS**
   - One user can have many farm locations
   - Line from USERS.uid to FARM_LOCATIONS.user_id

4. **PRODUCTS (N) ──── (M) ORDERS**
   - Many-to-many through items array
   - Crow's foot notation on both ends
   - Label: "N:M" or "*:*"

## Notation:
- PK = Primary Key (bold or underlined)
- FK = Foreign Key (italic or marked with arrow)
- Use crow's foot for cardinality:
  - One: Single line
  - Many: Three lines (crow's foot)

---

# DIAGRAM 8: SYSTEM ARCHITECTURE

## Layers (Horizontal rectangles, stacked):

### Layer 1: CLIENT LAYER (Top)
```
┌────────────────────────────────────┐
│  Desktop │  Tablet  │   Mobile    │
│  Browser │  Browser │   Browser   │
└──────────┴──────────┴──────────────┘
          ↓ HTTPS ↓
```

### Layer 2: PRESENTATION LAYER
```
┌────────────────────────────────────┐
│    Django Templates                │
│  Admin │  User  │  Guest  Views    │
│                                    │
│ HTML5, TailwindCSS, Alpine.js      │
└────────────────────────────────────┘
```

### Layer 3: APPLICATION LAYER
```
┌────────────────────────────────────┐
│        Django 5.1 Framework        │
│                                    │
│  ┌──────────────────────────────┐ │
│  │  Middleware (Auth, RBAC)     │ │
│  └──────────────────────────────┘ │
│                                    │
│  ┌──────────────────────────────┐ │
│  │  Views (Auth, Scan, Shop)    │ │
│  └──────────────────────────────┘ │
│                                    │
│  ┌──────────────────────────────┐ │
│  │  Services (Firebase, AI)     │ │
│  └──────────────────────────────┘ │
└────────────────────────────────────┘
```

### Layer 4: DATA LAYER
```
┌────────────────────────────────────┐
│  Firebase  │ Cloudinary │ Session  │
│  Firestore │    CDN     │ Storage  │
└────────────────────────────────────┘
```

### Layer 5: DEPLOYMENT LAYER (Bottom)
```
┌────────────────────────────────────┐
│        Render Platform             │
│   Gunicorn Server (2 workers)      │
│   512MB RAM, 0.1 CPU               │
└────────────────────────────────────┘
```

### Arrows:
- Vertical arrows between layers showing data flow
- Label arrows with protocols (HTTPS, REST API, etc.)

---

# COLOR CODING SUGGESTIONS

## For Use Case Diagram:
- **Guest actions:** Blue
- **User actions:** Orange
- **Admin actions:** Green
- **System boundary:** Black
- **External systems:** Purple

## For Activity Diagrams:
- **Start/End:** Black filled circles
- **Activities:** Light blue rectangles
- **Decisions:** Yellow diamonds
- **Swimlanes:** Alternate gray/white

## For Context Diagram:
- **System:** Orange center
- **Actors:** Blue stick figures
- **External services:** Green boxes
- **Arrows:** Black with labels

## For DFD:
- **Processes:** Blue circles
- **Data stores:** Green parallel lines
- **External entities:** Red rectangles
- **Data flows:** Black arrows with labels

## For ERD:
- **Primary Keys:** Bold red
- **Foreign Keys:** Blue italic
- **Regular fields:** Black
- **Relationships:** Black lines with cardinality

---

# TIPS FOR PROFESSIONAL DIAGRAMS

1. **Consistency:**
   - Use same colors for same elements across diagrams
   - Keep font sizes consistent (12-14pt for text, 10pt for labels)

2. **Alignment:**
   - Align elements using grid
   - Keep equal spacing between elements

3. **Clarity:**
   - Don't overcrowd diagrams
   - Use clear, concise labels
   - Avoid crossing lines when possible

4. **Legend:**
   - Include legend for symbols
   - Add title and date to each diagram

5. **Tools:**
   - **Draw.io:** Free, web-based
   - **Lucidchart:** Professional, templates
   - **Visio:** Microsoft, enterprise
   - **PlantUML:** Code-based diagrams

---

# EXPORTING TO WORD

### From Draw.io:
1. File → Export As → PNG/PDF
2. Insert into Word document
3. Add captions below each diagram

### From Lucidchart:
1. Share → Export → Microsoft Word
2. Automatically formats diagrams

### In Word:
1. Insert → Pictures → Select exported diagram
2. Right-click → Insert Caption
3. Format with borders and spacing

---

**These diagrams match the documentation in SYSTEM_DOCUMENTATION.md**
**Create them in your preferred tool and insert into your Word document!**
