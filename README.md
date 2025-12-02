
# 🍽️ Restaurant Website (Django)

A full-stack restaurant web application built with **Django**.  
This project allows customers to:

- 📰 View restaurant news feeds (announcements, promotions, updates)
- 🍔 Browse the menu
- 🛒 Place orders online
- 🔐 Create accounts and log in
- ⭐ Earn and redeem points with a rewards system
- 📜 Track their order history and rewards

---

## 🚀 Features

- **Authentication**: Customers can sign up, log in, and log out securely.
- **Feeds**: Admin can post news updates via Django’s built-in admin panel.
- **Menu Management**: Menu items are stored in the database and displayed dynamically.
- **Ordering System**: Customers place orders, earn points (10% of item price), and redeem points.
- **Rewards Tiers**:
  - 100 points → Free Dessert 🍰
  - 250 points → Free Main Dish 🍝
  - 500 points → VIP Status 🎉 (10% off all orders)
- **Order History**: Customers can view past orders, points earned, and rewards unlocked.

---

## 📂 Project Structure

restaurant_site/
│── manage.py
│── restaurant_site/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
│── restaurant/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── signals.py
│   ├── migrations/
│   │    └── __init__.py
│   └── templates/
│        ├── base.html
│        ├── index.html
│        ├── menu.html
│        ├── order.html
│        ├── feeds.html
│        ├── login.html
│        ├── signup.html
│        └── order_history.html
