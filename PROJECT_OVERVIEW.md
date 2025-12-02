# 🍽️ Restaurant Website - Project Overview

## 📋 Table of Contents
1. [Project Description](#project-description)
2. [Technology Stack](#technology-stack)
3. [Architecture](#architecture)
4. [Database Schema](#database-schema)
5. [Features Breakdown](#features-breakdown)
6. [User Flows](#user-flows)
7. [API Endpoints](#api-endpoints)
8. [File Structure](#file-structure)

---

## Project Description

A full-featured restaurant web application that enables customers to browse menus, place orders, and earn rewards. The system includes a comprehensive rewards program where customers earn 10% back in points on every purchase and can redeem these points for free items or VIP status.

### Key Highlights
- **Full-stack Django application** with modern UI
- **Rewards system** with three tiers (100, 250, 500 points)
- **VIP program** offering 10% discount on all orders
- **Order tracking** with status updates
- **News feed system** for announcements and promotions
- **Admin dashboard** for complete restaurant management

---

## Technology Stack

### Backend
- **Framework**: Django 4.2+
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Authentication**: Django's built-in authentication system
- **Media Handling**: Pillow for image processing

### Frontend
- **Templates**: Django Template Language (DTL)
- **Styling**: Custom CSS with gradient designs
- **JavaScript**: Vanilla JS for dynamic interactions
- **Responsive**: Mobile-friendly design

### Additional Tools
- **Admin Panel**: Django Admin (customized)
- **Signals**: Automatic profile creation
- **Validators**: Built-in Django validators

---

## Architecture

### MVC Pattern (Model-View-Template in Django)

```
┌─────────────────────────────────────────┐
│           User Interface                │
│  (HTML Templates + CSS + JavaScript)    │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│           URL Routing                   │
│        (urls.py files)                  │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│           Views Layer                   │
│  (Business Logic - views.py)            │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│           Models Layer                  │
│  (Database Models - models.py)          │
└────────────────┬────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────┐
│           Database                      │
│  (SQLite / PostgreSQL)                  │
└─────────────────────────────────────────┘
```

### Component Architecture

```
Restaurant Website
│
├── Authentication Module
│   ├── User Registration
│   ├── Login/Logout
│   └── Profile Management
│
├── Menu Module
│   ├── Category Management
│   ├── Menu Item Display
│   └── Availability Status
│
├── Order Module
│   ├── Cart System
│   ├── Order Processing
│   ├── Order History
│   └── Status Tracking
│
├── Rewards Module
│   ├── Points Calculation (10% back)
│   ├── Points Tracking
│   ├── Reward Redemption
│   └── VIP Management
│
└── News Module
    ├── Feed Display
    ├── Admin Management
    └── Announcement System
```

---

## Database Schema

### Core Models

#### 1. User (Django Built-in)
```python
- username: CharField
- email: EmailField
- password: CharField (hashed)
- date_joined: DateTimeField
```

#### 2. CustomerProfile
```python
- user: OneToOneField → User
- phone: CharField
- address: TextField
- points: IntegerField (default: 0)
- is_vip: BooleanField (default: False)
- vip_since: DateTimeField (nullable)
```

#### 3. Category
```python
- name: CharField
- description: TextField
- order: IntegerField (for sorting)
```

#### 4. MenuItem
```python
- name: CharField
- description: TextField
- price: DecimalField
- category: ForeignKey → Category
- image: ImageField
- is_available: BooleanField
- created_at: DateTimeField
- updated_at: DateTimeField
```

#### 5. Order
```python
- customer: ForeignKey → User
- status: CharField (choices)
  * pending
  * confirmed
  * preparing
  * ready
  * delivered
  * cancelled
- total_amount: DecimalField
- points_earned: IntegerField
- discount_applied: DecimalField
- special_instructions: TextField
- created_at: DateTimeField
- updated_at: DateTimeField
```

#### 6. OrderItem
```python
- order: ForeignKey → Order
- menu_item: ForeignKey → MenuItem
- quantity: PositiveIntegerField
- price: DecimalField
- subtotal: DecimalField
```

#### 7. Reward
```python
- name: CharField
- description: TextField
- points_required: IntegerField
- tier: IntegerField
- is_active: BooleanField
```

#### 8. RewardRedemption
```python
- customer: ForeignKey → User
- reward: ForeignKey → Reward
- points_spent: IntegerField
- redeemed_at: DateTimeField
- order: ForeignKey → Order (nullable)
```

#### 9. NewsFeed
```python
- title: CharField
- content: TextField
- image: ImageField
- created_at: DateTimeField
- updated_at: DateTimeField
- is_active: BooleanField
```

### Database Relationships

```
User ──1:1── CustomerProfile
  │
  ├──1:N── Order ──1:N── OrderItem ──N:1── MenuItem
  │                                           │
  └──1:N── RewardRedemption ──N:1── Reward   │
                                              │
Category ──1:N── MenuItem                     │
                                              │
NewsFeed (standalone)                         │
```

---

## Features Breakdown

### 1. Authentication System
**Features:**
- User registration with validation
- Secure login/logout
- Password hashing
- Session management
- Automatic profile creation via signals

**User Types:**
- Regular customers (authenticated users)
- Admin users (superusers)

### 2. Menu Browsing
**Features:**
- Category-based organization
- Search by category
- Item availability status
- Price display
- Item descriptions and images
- Responsive grid layout

### 3. Ordering System
**Features:**
- Multi-item selection
- Quantity adjustment
- Real-time price calculation
- Special instructions field
- VIP discount application
- Points earned display
- Order confirmation

**Order Processing:**
1. Customer selects items and quantities
2. System calculates subtotal
3. VIP discount applied (if applicable)
4. Points calculated (10% of subtotal)
5. Order saved to database
6. Points added to customer profile
7. Confirmation message displayed

### 4. Rewards Program
**Tiers:**
- **Tier 1** (100 points): Free Dessert 🍰
- **Tier 2** (250 points): Free Main Dish 🍝
- **Tier 3** (500 points): VIP Status 🎉

**Points System:**
- Earn: 10% back on every purchase
- Track: View current points in profile
- Redeem: Exchange for rewards
- VIP Benefit: 10% discount on all future orders

**VIP System:**
- Unlocked at 500 points
- Permanent status
- 10% discount on all orders
- Special badge display

### 5. Order History
**Features:**
- Complete order list
- Order status tracking
- Points earned per order
- Redemption history
- Total spent tracking
- Date and time stamps

### 6. News Feed
**Features:**
- Announcements display
- Promotional content
- Image support
- Date-sorted display
- Admin-managed content

### 7. Admin Dashboard
**Management Features:**
- Menu item management
- Category management
- Order status updates
- Customer profile viewing
- News feed posting
- Reward configuration
- User management

---

## User Flows

### Customer Registration & First Order
```
1. Visit Homepage → 2. Click "Sign Up"
         ↓
3. Fill Registration Form → 4. Create Account
         ↓
5. Auto Login → 6. View Menu
         ↓
7. Select Items → 8. Place Order
         ↓
9. Earn Points → 10. View Confirmation
```

### Reward Redemption Flow
```
1. Accumulate Points → 2. View Available Rewards
         ↓
3. Select Reward → 4. Redeem Points
         ↓
5. Points Deducted → 6. Reward Confirmed
```

### VIP Status Achievement
```
1. Regular Customer → 2. Place Orders
         ↓
3. Earn Points → 4. Reach 500 Points
         ↓
5. Auto VIP Status → 6. Get 10% Discount
         ↓
7. All Future Orders → 8. Discounted
```

---

## API Endpoints

### Public URLs (No Authentication Required)
| URL | Method | Description |
|-----|--------|-------------|
| `/` | GET | Homepage with featured items |
| `/menu/` | GET | Menu listing with categories |
| `/feeds/` | GET | News feeds |
| `/login/` | GET, POST | User login |
| `/signup/` | GET, POST | User registration |

### Protected URLs (Authentication Required)
| URL | Method | Description |
|-----|--------|-------------|
| `/order/` | GET, POST | Place new order |
| `/order-history/` | GET | View order history & rewards |
| `/profile/` | GET, POST | View/edit profile |
| `/redeem/<id>/` | POST | Redeem reward |
| `/logout/` | GET | User logout |

### Admin URLs
| URL | Method | Description |
|-----|--------|-------------|
| `/admin/` | GET, POST | Django admin panel |

---

## File Structure

```
restaurant_site/
│
├── manage.py                          # Django CLI utility
├── requirements.txt                   # Python dependencies
├── README.md                          # Full documentation
├── SETUP.md                           # Setup instructions
├── QUICKSTART.txt                     # Quick start guide
├── populate_sample_data.py           # Sample data script
│
├── restaurant_site/                   # Project configuration
│   ├── __init__.py
│   ├── settings.py                   # Django settings
│   ├── urls.py                       # Main URL routing
│   ├── wsgi.py                       # WSGI configuration
│   └── asgi.py                       # ASGI configuration
│
├── restaurant/                        # Main application
│   ├── __init__.py
│   ├── admin.py                      # Admin configuration
│   ├── apps.py                       # App configuration
│   ├── models.py                     # Database models
│   ├── views.py                      # View functions
│   ├── urls.py                       # App URL patterns
│   ├── signals.py                    # Signal handlers
│   │
│   ├── migrations/                   # Database migrations
│   │   └── __init__.py
│   │
│   ├── templates/                    # HTML templates
│   │   ├── base.html                # Base template
│   │   ├── index.html               # Homepage
│   │   ├── menu.html                # Menu page
│   │   ├── order.html               # Order page
│   │   ├── order_history.html       # History page
│   │   ├── feeds.html               # News page
│   │   ├── login.html               # Login page
│   │   ├── signup.html              # Signup page
│   │   └── profile.html             # Profile page
│   │
│   └── static/                       # Static files (CSS/JS)
│
└── media/                            # User-uploaded files
    ├── menu_items/                   # Menu images
    └── news/                         # News images
```

---

## Development Workflow

### Adding New Features

1. **Model Changes**
   ```bash
   # Edit models.py
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **View Creation**
   ```python
   # Add view in views.py
   # Add URL in urls.py
   # Create template in templates/
   ```

3. **Admin Integration**
   ```python
   # Register model in admin.py
   @admin.register(ModelName)
   class ModelNameAdmin(admin.ModelAdmin):
       list_display = [...]
   ```

### Testing Checklist
- [ ] User registration works
- [ ] Login/logout functional
- [ ] Menu displays correctly
- [ ] Orders process successfully
- [ ] Points accumulate correctly
- [ ] VIP status triggers at 500 points
- [ ] Admin panel accessible
- [ ] Responsive on mobile

---

## Security Considerations

### Implemented
- ✓ Password hashing
- ✓ CSRF protection
- ✓ SQL injection prevention (ORM)
- ✓ XSS protection (template escaping)
- ✓ Login required decorators
- ✓ Form validation

### For Production
- Change SECRET_KEY
- Set DEBUG = False
- Configure ALLOWED_HOSTS
- Use HTTPS
- Set up proper CORS
- Implement rate limiting
- Add email verification
- Set up proper logging

---

## Performance Optimization

### Implemented
- Database indexing on foreign keys
- Query optimization with select_related/prefetch_related
- Efficient template rendering
- Static file optimization

### Recommendations
- Add database caching (Redis/Memcached)
- Implement CDN for static files
- Use Gunicorn/uWSGI for production
- Set up database connection pooling
- Add pagination for large lists

---

## Future Enhancement Ideas

1. **Payment Integration**
   - Stripe/PayPal integration
   - Multiple payment methods
   - Order invoicing

2. **Delivery System**
   - Real-time order tracking
   - Delivery driver assignment
   - GPS tracking

3. **Communication**
   - Email notifications
   - SMS alerts
   - Push notifications

4. **Social Features**
   - Reviews and ratings
   - Share orders on social media
   - Referral program

5. **Advanced Features**
   - Table reservations
   - Multiple locations
   - Loyalty tiers beyond VIP
   - Scheduled orders

---

## Conclusion

This restaurant website is a production-ready Django application with a comprehensive feature set. It demonstrates best practices in Django development including proper MVC separation, database design, user authentication, and admin management.

The codebase is well-structured, documented, and ready for customization to fit specific business needs.

---

**For questions or support, refer to:**
- README.md - Complete documentation
- SETUP.md - Detailed setup guide
- Django Documentation - https://docs.djangoproject.com/

Happy coding! 🚀