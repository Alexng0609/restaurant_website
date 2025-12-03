from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db import transaction
from .models import (
    MenuItem,
    Category,
    NewsFeed,
    Order,
    OrderItem,
    CustomerProfile,
    Reward,
    RewardRedemption,
)
from decimal import Decimal


def index(request):
    """Homepage view"""
    latest_news = NewsFeed.objects.filter(is_active=True)[:3]
    featured_items = MenuItem.objects.filter(is_available=True)[:6]

    context = {
        "latest_news": latest_news,
        "featured_items": featured_items,
    }
    return render(request, "index.html", context)


def feeds(request):
    """News feeds view"""
    news_feeds = NewsFeed.objects.filter(is_active=True)
    context = {
        "news_feeds": news_feeds,
    }
    return render(request, "feeds.html", context)


def menu(request):
    """Menu view with categories"""
    categories = Category.objects.prefetch_related("items").all()
    selected_category = request.GET.get("category")

    if selected_category:
        menu_items = MenuItem.objects.filter(
            category_id=selected_category, is_available=True
        )
    else:
        menu_items = MenuItem.objects.filter(is_available=True)

    context = {
        "categories": categories,
        "menu_items": menu_items,
        "selected_category": selected_category,
    }
    return render(request, "menu.html", context)


@login_required
def place_order(request):
    """Order placement view"""
    if request.method == "POST":
        try:
            with transaction.atomic():
                # Create the order
                order = Order.objects.create(
                    customer=request.user,
                    special_instructions=request.POST.get("special_instructions", ""),
                )

                # Get cart items from POST data
                cart_items = []
                for key, value in request.POST.items():
                    if key.startswith("quantity_"):
                        item_id = key.replace("quantity_", "")
                        quantity = int(value)
                        if quantity > 0:
                            menu_item = get_object_or_404(MenuItem, id=item_id)
                            cart_items.append({"item": menu_item, "quantity": quantity})

                if not cart_items:
                    messages.error(request, "Please add items to your cart.")
                    return redirect("menu")

                # Create order items
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        menu_item=cart_item["item"],
                        quantity=cart_item["quantity"],
                    )

                # Calculate total and points
                order.calculate_total()

                # Add points to customer profile
                if hasattr(request.user, "profile"):
                    request.user.profile.add_points(order.points_earned)

                messages.success(
                    request,
                    f"Order placed successfully! You earned {order.points_earned} points. "
                    f"Total: ${order.total_amount}",
                )
                return redirect("order_history")

        except Exception as e:
            messages.error(request, f"Error placing order: {str(e)}")
            return redirect("menu")

    # GET request - show order form
    categories = Category.objects.prefetch_related("items").all()
    menu_items = MenuItem.objects.filter(is_available=True)

    # Get customer profile for VIP status
    profile = None
    if hasattr(request.user, "profile"):
        profile = request.user.profile

    context = {
        "categories": categories,
        "menu_items": menu_items,
        "profile": profile,
    }
    return render(request, "order.html", context)


@login_required
def order_history(request):
    """View order history and rewards"""
    orders = Order.objects.filter(customer=request.user).prefetch_related(
        "items__menu_item"
    )
    profile = get_object_or_404(CustomerProfile, user=request.user)
    available_rewards = profile.get_available_rewards()
    redemptions = RewardRedemption.objects.filter(customer=request.user)

    context = {
        "orders": orders,
        "profile": profile,
        "available_rewards": available_rewards,
        "redemptions": redemptions,
    }
    return render(request, "order_history.html", context)


@login_required
def redeem_reward(request, reward_id):
    """Redeem a reward"""
    if request.method == "POST":
        reward = get_object_or_404(Reward, id=reward_id, is_active=True)
        profile = request.user.profile

        if profile.points >= reward.points_required:
            with transaction.atomic():
                profile.redeem_points(reward.points_required)
                RewardRedemption.objects.create(
                    customer=request.user,
                    reward=reward,
                    points_spent=reward.points_required,
                )
                messages.success(request, f"Successfully redeemed: {reward.name}!")
        else:
            messages.error(request, "Not enough points to redeem this reward.")

    return redirect("order_history")


def signup_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        from .forms import CustomSignUpForm

        form = CustomSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(
                request,
                f"Tài khoản đã được tạo cho {username}! Bạn có thể đăng nhập ngay.",
            )
            login(request, user)
            return redirect("index")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        from .forms import CustomSignUpForm

        form = CustomSignUpForm()

    return render(request, "signup.html", {"form": form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                next_url = request.GET.get("next", "index")
                return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("index")


@login_required
def profile_view(request):
    """User profile view"""
    profile = get_object_or_404(CustomerProfile, user=request.user)

    if request.method == "POST":
        profile.phone = request.POST.get("phone", "")
        profile.address = request.POST.get("address", "")
        profile.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    context = {
        "profile": profile,
    }
    return render(request, "profile.html", context)


# Add these new views to your views.py file


@login_required
def checkout(request):
    """Checkout page with delivery address and payment"""
    # Get customer profile
    profile = None
    if hasattr(request.user, "profile"):
        profile = request.user.profile

    if request.method == "POST":
        try:
            with transaction.atomic():
                # Get delivery information
                customer_name = request.POST.get("customer_name", "").strip()
                phone = request.POST.get("phone", "").strip()
                delivery_address = request.POST.get("delivery_address", "").strip()
                payment_method = request.POST.get("payment_method", "").strip()
                special_instructions = request.POST.get(
                    "special_instructions", ""
                ).strip()

                # Validate required fields
                if not all([customer_name, phone, delivery_address, payment_method]):
                    messages.error(request, "Vui lòng điền đầy đủ thông tin giao hàng!")
                    return redirect("checkout")

                # Create the order
                order = Order.objects.create(
                    customer=request.user,
                    customer_name=customer_name,
                    phone=phone,
                    delivery_address=delivery_address,
                    payment_method=payment_method,
                    special_instructions=special_instructions,
                )

                # Get cart items from POST data
                cart_items = []
                for key, value in request.POST.items():
                    if key.startswith("quantity_"):
                        item_id = key.replace("quantity_", "")
                        quantity = int(value)
                        if quantity > 0:
                            menu_item = get_object_or_404(MenuItem, id=item_id)
                            cart_items.append({"item": menu_item, "quantity": quantity})

                if not cart_items:
                    order.delete()
                    messages.error(request, "Giỏ hàng trống!")
                    return redirect("menu")

                # Create order items
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        menu_item=cart_item["item"],
                        quantity=cart_item["quantity"],
                    )

                # Calculate total and points
                order.calculate_total()

                # Add points to customer profile
                if profile:
                    profile.add_points(order.points_earned)

                # Update profile address if empty
                if profile and not profile.address:
                    profile.address = delivery_address
                    profile.phone = phone
                    profile.save()

                # Payment method message
                payment_msg = {
                    "bank": "Vui lòng chuyển khoản theo thông tin đã cung cấp.",
                    "momo": "Vui lòng thanh toán qua MoMo theo thông tin đã cung cấp.",
                    "cod": "Bạn sẽ thanh toán khi nhận hàng.",
                }

                messages.success(
                    request,
                    f"Đặt hàng thành công! Đơn hàng #{order.id}. "
                    f"{payment_msg.get(payment_method, '')} "
                    f"Bạn nhận được {order.points_earned} điểm thưởng!",
                )
                return redirect("order_history")

        except Exception as e:
            messages.error(request, f"Lỗi khi đặt hàng: {str(e)}")
            return redirect("checkout")

    # GET request
    context = {
        "profile": profile,
    }
    return render(request, "checkout.html", context)
