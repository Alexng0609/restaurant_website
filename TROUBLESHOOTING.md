# 🔧 Troubleshooting Guide

Common issues and their solutions for the Restaurant Website project.

---

## Installation Issues

### Problem: "No module named 'django'"
**Solution:**
```bash
pip install django pillow
```

### Problem: "No module named 'PIL'"
**Solution:**
```bash
pip install pillow
```

### Problem: Permission denied on manage.py
**Solution:**
```bash
# On macOS/Linux
chmod +x manage.py

# Or run with python explicitly
python manage.py runserver
```

---

## Database Issues

### Problem: "no such table: restaurant_menuitem"
**Solution:** Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Problem: "UNIQUE constraint failed"
**Solution:** Database already has duplicate data
```bash
# Option 1: Delete database and start fresh
# Delete db.sqlite3 file, then:
python manage.py migrate
python manage.py createsuperuser

# Option 2: Clear specific data via Django shell
python manage.py shell
>>> from restaurant.models import MenuItem
>>> MenuItem.objects.all().delete()
>>> exit()
```

### Problem: Migration conflicts
**Solution:** Reset migrations
```bash
# Backup your data first!
# Delete all migrations except __init__.py
# Then:
python manage.py makemigrations
python manage.py migrate
```

---

## Server Issues

### Problem: "Port already in use"
**Solution:**
```bash
# Run on different port
python manage.py runserver 8080

# Or kill the process using port 8000 (macOS/Linux)
lsof -ti:8000 | xargs kill -9

# Or kill the process using port 8000 (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F
```

### Problem: Static files not loading
**Solution:**
```bash
# In settings.py, ensure:
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'restaurant' / 'static']

# Then run:
python manage.py collectstatic
```

### Problem: Media files not showing
**Solution:**
```bash
# 1. Create media directories
mkdir media/menu_items
mkdir media/news

# 2. Check settings.py has:
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 3. Check urls.py includes media serving in DEBUG mode
```

---

## Authentication Issues

### Problem: "Can't log in with superuser"
**Solution:**
```bash
# Reset superuser password
python manage.py changepassword <username>

# Or create new superuser
python manage.py createsuperuser
```

### Problem: "User has no profile"
**Solution:** The signal should create profiles automatically, but if needed:
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User
from restaurant.models import CustomerProfile

for user in User.objects.all():
    if not hasattr(user, 'profile'):
        CustomerProfile.objects.create(user=user)
        print(f"Created profile for {user.username}")
exit()
```

---

## Order Issues

### Problem: "Orders not calculating total correctly"
**Solution:** 
```python
# In Django shell:
python manage.py shell
```
```python
from restaurant.models import Order

# Recalculate all orders
for order in Order.objects.all():
    order.calculate_total()
    print(f"Order {order.id}: ${order.total_amount}")
exit()
```

### Problem: "Points not being awarded"
**Solution:** Check that order.calculate_total() is being called after order items are added.

---

## Admin Panel Issues

### Problem: "Can't access /admin/"
**Solution:**
```bash
# 1. Make sure you created a superuser
python manage.py createsuperuser

# 2. Check that INSTALLED_APPS includes 'django.contrib.admin'
# 3. Check that urls.py includes admin URLs
```

### Problem: "Images not showing in admin"
**Solution:**
```python
# In settings.py, add:
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# In main urls.py, add:
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## Template Issues

### Problem: "TemplateDoesNotExist"
**Solution:**
```python
# Check settings.py has:
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,  # This should be True
    ...
}]

# Verify template is in: restaurant/templates/
```

### Problem: "Static files not loading in templates"
**Solution:**
```django
# At top of template, add:
{% load static %}

# Then use:
<link rel="stylesheet" href="{% static 'css/style.css' %}">
```

---

## Data Issues

### Problem: "Sample data script not working"
**Solution:**
```bash
# Run the script properly:
python manage.py shell < populate_sample_data.py

# Or run manually:
python manage.py shell
# Then paste the contents of populate_sample_data.py
```

### Problem: "Categories not showing in menu"
**Solution:**
```python
python manage.py shell
```
```python
from restaurant.models import Category, MenuItem

# Check if categories exist
print(Category.objects.all())

# Check if items exist
print(MenuItem.objects.all())

# Create test category if needed
Category.objects.create(name="Test Category", order=1)
exit()
```

---

## Performance Issues

### Problem: "Site is slow"
**Solutions:**
1. Use select_related() and prefetch_related() in queries
2. Add database indexes
3. Enable caching
4. Use pagination for large lists

```python
# Example optimization in views.py:
# Before (slow):
categories = Category.objects.all()

# After (fast):
categories = Category.objects.prefetch_related('items').all()
```

---

## Deployment Issues

### Problem: "DEBUG = False causes CSS to disappear"
**Solution:**
```bash
# Collect static files:
python manage.py collectstatic

# Configure static file serving in production
# Use WhiteNoise or configure web server (nginx/Apache)
```

### Problem: "Database locked" error
**Solution:** SQLite doesn't handle concurrent writes well
```python
# For production, switch to PostgreSQL:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'restaurant_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## Error Messages Explained

### "CSRF verification failed"
- You forgot {% csrf_token %} in your form
- Or cookies are disabled in browser

### "Object has no attribute 'profile'"
- User object doesn't have a CustomerProfile
- Run the profile creation script in Authentication Issues section

### "Invalid block tag"
- Missing {% load static %} or {% load custom_tags %}
- Misspelled template tag

### "MultiValueDictKeyError"
- Form field name in template doesn't match view
- Or required field is missing from form

---

## Quick Diagnostic Commands

```bash
# Check Python version
python --version

# Check Django version
python -m django --version

# Check installed packages
pip list

# Run tests
python manage.py test

# Check for missing migrations
python manage.py showmigrations

# Validate project
python manage.py check

# Open shell to test queries
python manage.py shell

# See all URLs
python manage.py show_urls  # (requires django-extensions)
```

---

## Getting Help

If you're still stuck:

1. **Check the error message carefully** - Django's error pages are very helpful
2. **Check Django documentation** - https://docs.djangoproject.com/
3. **Search Stack Overflow** - Most Django errors have been encountered before
4. **Check the logs** - Look at console output when running server
5. **Read the code comments** - This project has detailed comments

---

## Common Commands Reference

```bash
# Development
python manage.py runserver
python manage.py shell
python manage.py dbshell

# Database
python manage.py makemigrations
python manage.py migrate
python manage.py sqlmigrate restaurant 0001

# Admin
python manage.py createsuperuser
python manage.py changepassword <username>

# Static Files
python manage.py collectstatic
python manage.py findstatic <filename>

# Testing
python manage.py test
python manage.py test restaurant

# Utilities
python manage.py check
python manage.py showmigrations
python manage.py dumpdata > backup.json
python manage.py loaddata backup.json
```

---

## Prevention Tips

1. **Always use virtual environment**
2. **Keep requirements.txt updated**
3. **Make migrations after model changes**
4. **Test locally before deploying**
5. **Backup database regularly**
6. **Keep Django and packages updated**
7. **Never commit SECRET_KEY to version control**
8. **Use environment variables for sensitive data**

---

**Remember:** Most issues can be solved by:
1. Reading the error message carefully
2. Checking the documentation
3. Running migrations
4. Restarting the development server

Good luck! 🚀