from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
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


def feed_detail(request, news_id):
    """Single news feed detail view"""
    news = get_object_or_404(NewsFeed, id=news_id, is_active=True)

    # Get related news (exclude current, get 3 most recent)
    related_news = NewsFeed.objects.filter(is_active=True).exclude(id=news_id)[:3]

    context = {
        "news": news,
        "related_news": related_news,
    }
    return render(request, "feed_detail.html", context)


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
                    messages.error(request, "Vui lòng thêm món vào giỏ hàng.")
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
                    f"Đặt hàng thành công! Bạn nhận được {order.points_earned:,.0f} điểm. "
                    f"Tổng: {order.total_amount:,.0f} ₫",
                )
                return redirect("order_history")

        except Exception as e:
            messages.error(request, f"Lỗi khi đặt hàng: {str(e)}")
            return redirect("menu")

    # GET request - show order form
    categories = Category.objects.prefetch_related("items").all()
    menu_items = MenuItem.objects.filter(is_available=True)

    # Get customer profile
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

                # Apply discount if available
                discount_info = request.session.get("pending_discount")
                if discount_info:
                    order.calculate_total(apply_discount=discount_info)
                    del request.session["pending_discount"]
                else:
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
                    f"Bạn nhận được {order.points_earned:,.0f} điểm thưởng!",
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


@login_required
def order_history(request):
    """View order history and rewards"""
    profile = request.user.profile
    orders = Order.objects.filter(customer=request.user)

    # Get reward redemptions
    redemptions = RewardRedemption.objects.filter(customer=request.user)

    context = {
        "profile": profile,
        "orders": orders,
        "redemptions": redemptions,
    }
    return render(request, "order_history.html", context)


@login_required
def redeem_discount(request):
    """Redeem discount - 5% (50k points) or 10% (100k points)"""
    if request.method == "POST":
        profile = request.user.profile
        discount_type = request.POST.get("discount_type")

        if discount_type == "5percent":
            required_points = 50000
            discount_value = 0.05
            label = "Giảm giá 5%"
        elif discount_type == "10percent":
            required_points = 100000
            discount_value = 0.10
            label = "Giảm giá 10%"
        else:
            messages.error(request, "❌ Loại giảm giá không hợp lệ.")
            return redirect("order_history")

        if profile.points >= required_points:
            # Deduct points
            profile.points -= required_points
            profile.save()

            # Store discount in session for next order
            request.session["pending_discount"] = {
                "type": discount_type,
                "value": discount_value,
                "label": label,
            }

            messages.success(
                request,
                f"🎉 Đã đổi thành công! {label} sẽ được áp dụng cho đơn hàng tiếp theo.",
            )
        else:
            needed = required_points - profile.points
            messages.error(
                request, f"❌ Bạn cần thêm {needed:,.0f} điểm nữa để đổi ưu đãi này."
            )

    return redirect("order_history")


@login_required
def redeem_reward(request, reward_id=None):
    """Redeem free item - Phần Đậm Ấm (20k points)"""
    if request.method == "POST":
        profile = request.user.profile
        reward_type = request.POST.get("reward_type")

        if reward_type == "phan_dam_am":
            required_points = 200000
            reward_name = "Phần Đậm Ấm"
            reward_value = 149000

            if profile.points >= required_points:
                # Deduct points
                profile.points -= required_points
                profile.save()

                # Store reward in session
                request.session["pending_reward"] = {
                    "type": "phan_dam_am",
                    "name": reward_name,
                    "value": reward_value,
                }

                messages.success(
                    request,
                    f"🍲 Đã đổi thành công! {reward_name} (trị giá {reward_value:,.0f} ₫) "
                    f"sẽ được tự động thêm vào đơn hàng tiếp theo.",
                )
            else:
                needed = required_points - profile.points
                messages.error(
                    request,
                    f"❌ Bạn cần thêm {needed:,.0f} điểm nữa để đổi phần thưởng này.",
                )
        else:
            messages.error(request, "❌ Loại phần thưởng không hợp lệ.")

    return redirect("order_history")


def signup_view(request):
    """User registration - matches urls.py name"""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create customer profile
            CustomerProfile.objects.create(user=user)
            username = form.cleaned_data.get("username")
            messages.success(request, f"Tài khoản đã được tạo cho {username}!")
            login(request, user)
            return redirect("index")
    else:
        form = UserCreationForm()

    return render(request, "register.html", {"form": form})


def login_view(request):
    """User login - matches urls.py name"""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Chào mừng trở lại, {username}!")
                return redirect("index")
            else:
                messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.")
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không đúng.")
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})


@login_required
def logout_view(request):
    """User logout - matches urls.py name"""
    logout(request)
    messages.success(request, "Bạn đã đăng xuất.")
    return redirect("index")


@login_required
def profile_view(request):
    """User profile view - matches urls.py name"""
    profile = request.user.profile

    if request.method == "POST":
        # Update profile
        profile.phone = request.POST.get("phone", "")
        profile.address = request.POST.get("address", "")
        profile.save()

        messages.success(request, "Hồ sơ đã được cập nhật!")
        return redirect("profile")

    context = {
        "profile": profile,
    }
    return render(request, "profile.html", context)
