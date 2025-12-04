from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    """Menu categories (e.g., Appetizers, Main Course, Desserts, Drinks)"""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0, help_text="Display order")

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """Menu items available for order"""

    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10, decimal_places=0, validators=[MinValueValidator(Decimal("0"))]
    )  # Updated for VND - supports up to 9,999,999,999
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="items"
    )
    image = models.ImageField(upload_to="menu_items/", blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.name} - {self.price:,.0f} ₫"


class NewsFeed(models.Model):
    """Restaurant news, announcements, and promotions"""

    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to="news/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "News Feed"
        verbose_name_plural = "News Feeds"

    def __str__(self):
        return self.title


class CustomerProfile(models.Model):
    """Extended user profile with rewards system"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    points = models.IntegerField(default=0)
    is_vip = models.BooleanField(default=False)
    vip_since = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def add_points(self, amount):
        """Add points and check for VIP status"""
        self.points += amount
        if self.points >= 500 and not self.is_vip:
            from django.utils import timezone

            self.is_vip = True
            self.vip_since = timezone.now()
        self.save()

    def redeem_points(self, amount):
        """Redeem points for rewards"""
        if self.points >= amount:
            self.points -= amount
            self.save()
            return True
        return False

    def get_available_rewards(self):
        """Get list of rewards the customer can redeem"""
        rewards = []
        if self.points >= 100:
            rewards.append({"name": "Free Dessert 🍰", "points": 100, "tier": 1})
        if self.points >= 250:
            rewards.append({"name": "Free Main Dish 🍝", "points": 250, "tier": 2})
        if self.points >= 500:
            rewards.append({"name": "VIP Status 🎉", "points": 500, "tier": 3})
        return rewards


class Order(models.Model):
    """Customer orders"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("preparing", "Preparing"),
        ("ready", "Ready"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=0, default=0
    )  # Updated for VND
    points_earned = models.IntegerField(default=0)
    discount_applied = models.DecimalField(
        max_digits=12, decimal_places=0, default=0
    )  # Updated for VND
    special_instructions = models.TextField(blank=True)
    customer_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    delivery_address = models.TextField(blank=True)
    payment_method = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ("bank", "Chuyển Khoản Ngân Hàng"),
            ("momo", "MoMo"),
            ("cod", "Thanh Toán Khi Nhận Hàng"),
        ],
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username} - {self.status}"

    def calculate_total(self, apply_discount=None):
        # Calculater order total from order items
        subtotal = sum(item.subtotal for item in self.items.all())

        # Apply discount from session (manual redemption)
        discount = 0
        if apply_discount:
            if apply_discount.get("type") == "5percent":
                discount = subtotal * Decimal("0.05")
            elif apply_discount.get("type") == "vip" or self.customer.profile.is_vip:
                discount = subtotal * Decimal("0.10")
            self.discount_applied = discount

        self.total_amount = subtotal - discount

        # Calculate points (10% of subtotal before discount)
        self.points_earned = int((subtotal * Decimal("0.10")).to_integral_value())

        self.save()
        return self.total_amount


class OrderItem(models.Model):
    """Individual items in an order"""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=0)  # Updated for VND
    subtotal = models.DecimalField(max_digits=12, decimal_places=0)  # Updated for VND

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"

    def save(self, *args, **kwargs):
        """Calculate subtotal before saving"""
        self.price = self.menu_item.price
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)


class Reward(models.Model):
    """Predefined rewards that customers can redeem"""

    name = models.CharField(max_length=100)
    description = models.TextField()
    points_required = models.IntegerField(validators=[MinValueValidator(1)])
    tier = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["points_required"]

    def __str__(self):
        return f"{self.name} ({self.points_required} points)"


class RewardRedemption(models.Model):
    """Track reward redemptions by customers"""

    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="redemptions"
    )
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    points_spent = models.IntegerField()
    redeemed_at = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-redeemed_at"]

    def __str__(self):
        return f"{self.customer.username} - {self.reward.name}"
