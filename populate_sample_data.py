"""
Script to populate the database with sample data for testing.
Run this after setting up the database.

Usage:
    python manage.py shell < populate_sample_data.py
"""

from restaurant.models import Category, MenuItem, Reward, NewsFeed
from decimal import Decimal


def populate_data():
    print("🚀 Starting data population...")

    # Create Categories
    print("\n📁 Creating categories...")
    appetizers, created = Category.objects.get_or_create(
        name="Appetizers", defaults={"order": 1, "description": "Start your meal right"}
    )
    if created:
        print(f"  ✓ Created: {appetizers.name}")

    mains, created = Category.objects.get_or_create(
        name="Main Courses",
        defaults={"order": 2, "description": "Our signature dishes"},
    )
    if created:
        print(f"  ✓ Created: {mains.name}")

    desserts, created = Category.objects.get_or_create(
        name="Desserts", defaults={"order": 3, "description": "Sweet endings"}
    )
    if created:
        print(f"  ✓ Created: {desserts.name}")

    drinks, created = Category.objects.get_or_create(
        name="Drinks", defaults={"order": 4, "description": "Refreshing beverages"}
    )
    if created:
        print(f"  ✓ Created: {drinks.name}")

    # Create Menu Items
    print("\n🍽️ Creating menu items...")

    menu_items = [
        # Appetizers
        {
            "name": "Caesar Salad",
            "description": "Fresh romaine lettuce with parmesan cheese, croutons, and Caesar dressing",
            "price": Decimal("8.99"),
            "category": appetizers,
        },
        {
            "name": "Mozzarella Sticks",
            "description": "Crispy breaded mozzarella served with marinara sauce",
            "price": Decimal("7.99"),
            "category": appetizers,
        },
        {
            "name": "Buffalo Wings",
            "description": "Spicy chicken wings with blue cheese dip",
            "price": Decimal("9.99"),
            "category": appetizers,
        },
        # Main Courses
        {
            "name": "Grilled Chicken",
            "description": "Tender chicken breast marinated with herbs and spices, served with vegetables",
            "price": Decimal("15.99"),
            "category": mains,
        },
        {
            "name": "Beef Steak",
            "description": "Premium 8oz ribeye steak cooked to perfection with mashed potatoes",
            "price": Decimal("24.99"),
            "category": mains,
        },
        {
            "name": "Salmon Fillet",
            "description": "Grilled salmon with lemon butter sauce and asparagus",
            "price": Decimal("19.99"),
            "category": mains,
        },
        {
            "name": "Spaghetti Carbonara",
            "description": "Classic Italian pasta with bacon, eggs, and parmesan",
            "price": Decimal("13.99"),
            "category": mains,
        },
        {
            "name": "Vegetable Stir Fry",
            "description": "Fresh vegetables in savory sauce with rice",
            "price": Decimal("11.99"),
            "category": mains,
        },
        # Desserts
        {
            "name": "Chocolate Lava Cake",
            "description": "Warm chocolate cake with a molten center, served with vanilla ice cream",
            "price": Decimal("7.99"),
            "category": desserts,
        },
        {
            "name": "New York Cheesecake",
            "description": "Creamy cheesecake with graham cracker crust and berry compote",
            "price": Decimal("6.99"),
            "category": desserts,
        },
        {
            "name": "Tiramisu",
            "description": "Classic Italian dessert with coffee-soaked ladyfingers and mascarpone",
            "price": Decimal("7.49"),
            "category": desserts,
        },
        # Drinks
        {
            "name": "Fresh Lemonade",
            "description": "House-made lemonade with fresh lemons",
            "price": Decimal("3.99"),
            "category": drinks,
        },
        {
            "name": "Iced Tea",
            "description": "Refreshing iced tea, sweetened or unsweetened",
            "price": Decimal("2.99"),
            "category": drinks,
        },
        {
            "name": "Cappuccino",
            "description": "Espresso with steamed milk and foam",
            "price": Decimal("4.49"),
            "category": drinks,
        },
        {
            "name": "Smoothie",
            "description": "Fresh fruit smoothie (strawberry, mango, or mixed berry)",
            "price": Decimal("5.99"),
            "category": drinks,
        },
    ]

    for item_data in menu_items:
        item, created = MenuItem.objects.get_or_create(
            name=item_data["name"],
            defaults={
                "description": item_data["description"],
                "price": item_data["price"],
                "category": item_data["category"],
                "is_available": True,
            },
        )
        if created:
            print(f"  ✓ Created: {item.name} - ${item.price}")

    # Create Rewards
    print("\n🎁 Creating rewards...")

    rewards = [
        {
            "name": "Free Dessert 🍰",
            "description": "Choose any dessert from our menu",
            "points_required": 100,
            "tier": 1,
        },
        {
            "name": "Free Main Dish 🍝",
            "description": "Choose any main course from our menu",
            "points_required": 250,
            "tier": 2,
        },
        {
            "name": "VIP Status 🎉",
            "description": "Unlock 10% discount on all future orders",
            "points_required": 500,
            "tier": 3,
        },
    ]

    for reward_data in rewards:
        reward, created = Reward.objects.get_or_create(
            name=reward_data["name"],
            defaults={
                "description": reward_data["description"],
                "points_required": reward_data["points_required"],
                "tier": reward_data["tier"],
                "is_active": True,
            },
        )
        if created:
            print(f"  ✓ Created: {reward.name} ({reward.points_required} points)")

    # Create News Feeds
    print("\n📰 Creating news feeds...")

    news_items = [
        {
            "title": "Grand Opening! 🎉",
            "content": "We're excited to announce our grand opening! Join us for special promotions and discounts. For a limited time, get 20% off your first order when you sign up for our rewards program!",
        },
        {
            "title": "New Menu Items Available",
            "content": "Check out our new seasonal menu featuring fresh local ingredients! We've added delicious new dishes including our signature salmon fillet and vegetable stir fry.",
        },
        {
            "title": "Rewards Program Announcement",
            "content": "Earn points with every purchase! Get 10% back in points on all orders. Redeem for free items or unlock VIP status for exclusive benefits.",
        },
    ]

    for news_data in news_items:
        news, created = NewsFeed.objects.get_or_create(
            title=news_data["title"],
            defaults={"content": news_data["content"], "is_active": True},
        )
        if created:
            print(f"  ✓ Created: {news.title}")

    print("\n✅ Sample data population completed!")
    print("\n📊 Summary:")
    print(f"  Categories: {Category.objects.count()}")
    print(f"  Menu Items: {MenuItem.objects.count()}")
    print(f"  Rewards: {Reward.objects.count()}")
    print(f"  News Feeds: {NewsFeed.objects.count()}")
    print("\n🌐 Visit http://127.0.0.1:8000/ to see your restaurant!")


# Run the population function
populate_data()
