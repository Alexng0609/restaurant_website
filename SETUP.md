# Quick Setup Guide 🚀

## Installation Steps

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Admin Account
```bash
python manage.py createsuperuser
```
Enter username, email (optional), and password when prompted.

### 4. Create Media Directories
```bash
# Windows
mkdir media\menu_items media\news

# macOS/Linux
mkdir -p media/menu_items media/news
```

### 5. Run Development Server
```bash
python manage.py runserver
```

### 6. Access the Application
- **Website**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

---

## Adding Sample Data

### Option 1: Through Admin Panel
1. Go to http://127.0.0.1:8000/admin/
2. Log in with superuser credentials
3. Add Categories (Appetizers, Main Courses, Desserts, Drinks)
4. Add Menu Items with prices and descriptions
5. Create News Feeds

### Option 2: Using Django Shell
```bash
python manage.py shell
```

Then paste:
```python
from restaurant.models import Category, MenuItem, Reward, NewsFeed
from decimal import Decimal

# Categories
appetizers = Category.objects.create(name="Appetizers", order=1, description="Start your meal right")
mains = Category.objects.create(name="Main Courses", order=2, description="Our signature dishes")
desserts = Category.objects.create(name="Desserts", order=3, description="Sweet endings")
drinks = Category.objects.create(name="Drinks", order=4, description="Refreshing beverages")

# Sample Menu Items
MenuItem.objects.create(
    name="Caesar Salad",
    description="Fresh romaine lettuce with parmesan cheese, croutons, and Caesar dressing",
    price=Decimal("8.99"),
    category=appetizers,
    is_available=True
)

MenuItem.objects.create(
    name="Grilled Chicken",
    description="Tender chicken breast marinated with herbs and spices, served with vegetables",
    price=Decimal("15.99"),
    category=mains,
    is_available=True
)

MenuItem.objects.create(
    name="Beef Steak",
    description="Premium 8oz ribeye steak cooked to perfection",
    price=Decimal("24.99"),
    category=mains,
    is_available=True
)

MenuItem.objects.create(
    name="Chocolate Lava Cake",
    description="Warm chocolate cake with a molten center, served with vanilla ice cream",
    price=Decimal("7.99"),
    category=desserts,
    is_available=True
)

MenuItem.objects.create(
    name="Fresh Lemonade",
    description="House-made lemonade with fresh lemons",
    price=Decimal("3.99"),
    category=drinks,
    is_available=True
)

# Rewards
Reward.objects.create(
    name="Free Dessert 🍰",
    description="Choose any dessert from our menu",
    points_required=100,
    tier=1,
    is_active=True
)

Reward.objects.create(
    name="Free Main Dish 🍝",
    description="Choose any main course from our menu",
    points_required=250,
    tier=2,
    is_active=True
)

Reward.objects.create(
    name="VIP Status 🎉",
    description="Unlock 10% discount on all future orders",
    points_required=500,
    tier=3,
    is_active=True
)

# Sample News Feed
NewsFeed.objects.create(
    title="Grand Opening!",
    content="We're excited to announce our grand opening! Join us for special promotions and discounts.",
    is_active=True
)

NewsFeed.objects.create(
    title="New Menu Items",
    content="Check out our new seasonal menu featuring fresh local ingredients!",
    is_active=True
)

print("✅ Sample data created successfully!")
exit()
```

---

## Testing the Application

### 1. Create a Customer Account
- Go to http://127.0.0.1:8000/signup/
- Create an account
- You'll start with 0 points

### 2. Browse Menu
- Go to http://127.0.0.1:8000/menu/
- View items by category

### 3. Place an Order
- Go to http://127.0.0.1:8000/order/
- Select quantities for items
- Submit order
- You'll earn 10% back in points!

### 4. Check Order History
- Go to http://127.0.0.1:8000/order-history/
- View your orders and points

### 5. Test Rewards System
- Place multiple orders to accumulate points
- At 100 points: Free dessert unlocked
- At 250 points: Free main dish unlocked
- At 500 points: VIP status (10% off all orders)

---

## Common Commands

```bash
# Create new migration after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Run on different port
python manage.py runserver 8080

# Open Django shell
python manage.py shell

# Collect static files (for production)
python manage.py collectstatic
```

---

## Project URLs

- **Homepage**: `/`
- **Menu**: `/menu/`
- **News**: `/feeds/`
- **Place Order**: `/order/`
- **Order History**: `/order-history/`
- **Profile**: `/profile/`
- **Login**: `/login/`
- **Signup**: `/signup/`
- **Admin Panel**: `/admin/`

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Setup database
3. ✅ Create admin account
4. ✅ Add sample data
5. ✅ Test the application
6. 📝 Customize for your needs
7. 🚀 Deploy to production

---

Good luck with your restaurant website! 🍽️