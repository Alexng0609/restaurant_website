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
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Q, Avg, F
from django.db.models.functions import TruncDate, TruncMonth, TruncYear
from datetime import datetime, timedelta
from django.db import models
import json
from django.contrib.auth.models import User


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


@staff_member_required
def admin_reports(request):
    """Admin reports view - daily, monthly, and annual reports"""

    # Get filter parameters
    report_type = request.GET.get("type", "daily")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # Set default date ranges
    today = timezone.now().date()
    if not start_date:
        if report_type == "daily":
            start_date = today
        elif report_type == "monthly":
            start_date = today.replace(day=1)
        else:  # annual
            start_date = today.replace(month=1, day=1)
    else:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

    if not end_date:
        end_date = today
    else:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    # Base queryset - orders within date range
    orders = Order.objects.filter(
        created_at__date__gte=start_date, created_at__date__lte=end_date
    ).exclude(status="cancelled")

    # Calculate summary statistics
    summary = {
        "total_orders": orders.count(),
        "total_revenue": orders.aggregate(Sum("total_amount"))["total_amount__sum"]
        or 0,
        "total_discount": orders.aggregate(Sum("discount_applied"))[
            "discount_applied__sum"
        ]
        or 0,
        "total_points_earned": orders.aggregate(Sum("points_earned"))[
            "points_earned__sum"
        ]
        or 0,
        "average_order_value": orders.aggregate(Avg("total_amount"))[
            "total_amount__avg"
        ]
        or 0,
    }

    # Orders with discount applied
    discounted_orders = orders.filter(discount_applied__gt=0)
    summary["discounted_orders_count"] = discounted_orders.count()
    summary["discount_usage_rate"] = (
        (summary["discounted_orders_count"] / summary["total_orders"] * 100)
        if summary["total_orders"] > 0
        else 0
    )

    # Top selling items
    top_items = (
        OrderItem.objects.filter(order__in=orders)
        .values("menu_item__name", "menu_item__category__name")
        .annotate(quantity_sold=Sum("quantity"), revenue=Sum("subtotal"))
        .order_by("-quantity_sold")[:10]
    )

    # Sales by category
    category_sales = (
        OrderItem.objects.filter(order__in=orders)
        .values("menu_item__category__name")
        .annotate(total_quantity=Sum("quantity"), total_revenue=Sum("subtotal"))
        .order_by("-total_revenue")
    )

    # Payment method breakdown
    payment_methods = (
        orders.values("payment_method")
        .annotate(count=Count("id"), revenue=Sum("total_amount"))
        .order_by("-count")
    )

    # Order status breakdown
    status_breakdown = (
        orders.values("status").annotate(count=Count("id")).order_by("-count")
    )

    # Time-based analysis
    if report_type == "daily":
        # Hourly breakdown for daily report
        hourly_sales = (
            orders.extra(select={"hour": "EXTRACT(hour FROM created_at)"})
            .values("hour")
            .annotate(orders_count=Count("id"), revenue=Sum("total_amount"))
            .order_by("hour")
        )

        time_data = list(hourly_sales)

    elif report_type == "monthly":
        # Daily breakdown for monthly report
        daily_sales = (
            orders.annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(orders_count=Count("id"), revenue=Sum("total_amount"))
            .order_by("date")
        )

        time_data = list(daily_sales)

    else:  # annual
        # Monthly breakdown for annual report
        monthly_sales = (
            orders.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(orders_count=Count("id"), revenue=Sum("total_amount"))
            .order_by("month")
        )

        time_data = list(monthly_sales)

    # Customer insights
    top_customers = (
        orders.values("customer__username", "customer__profile__points")
        .annotate(order_count=Count("id"), total_spent=Sum("total_amount"))
        .order_by("-total_spent")[:10]
    )

    # VIP customers who ordered
    vip_orders = orders.filter(customer__profile__is_vip=True)
    summary["vip_orders_count"] = vip_orders.count()
    summary["vip_revenue"] = (
        vip_orders.aggregate(Sum("total_amount"))["total_amount__sum"] or 0
    )

    # Discount breakdown
    discount_breakdown = {
        "5_percent": orders.filter(
            discount_applied__gt=0,
            discount_applied__lte=models.F("total_amount") * Decimal("0.06"),  # ~5%
        ).count(),
        "10_percent": orders.filter(
            discount_applied__gt=models.F("total_amount") * Decimal("0.06")  # ~10%
        ).count(),
    }

    # Convert querysets to JSON for charts
    chart_data = {
        "time_series": json.dumps(time_data, default=str),
        "category_sales": json.dumps(list(category_sales), default=str),
        "payment_methods": json.dumps(list(payment_methods), default=str),
        "status_breakdown": json.dumps(list(status_breakdown), default=str),
    }

    context = {
        "report_type": report_type,
        "start_date": start_date,
        "end_date": end_date,
        "summary": summary,
        "top_items": top_items,
        "category_sales": category_sales,
        "payment_methods": payment_methods,
        "status_breakdown": status_breakdown,
        "time_data": time_data,
        "top_customers": top_customers,
        "discount_breakdown": discount_breakdown,
        "chart_data": chart_data,
    }

    return render(request, "admin_reports.html", context)


@staff_member_required
def user_reports(request):
    """User Reports - Shows customer activity and spending"""

    # Get filter parameters
    search_query = request.GET.get("search", "")
    order_by = request.GET.get("order_by", "-total_spent")

    # Base queryset - all users with profiles
    users = User.objects.filter(profile__isnull=False).select_related("profile")

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query)
            | Q(email__icontains=search_query)
            | Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
        )

    # Annotate user statistics
    user_stats = []
    for user in users:
        orders = Order.objects.filter(customer=user).exclude(status="cancelled")

        total_orders = orders.count()
        total_spent = orders.aggregate(Sum("total_amount"))["total_amount__sum"] or 0
        total_discount_used = (
            orders.aggregate(Sum("discount_applied"))["discount_applied__sum"] or 0
        )
        orders_with_discount = orders.filter(discount_applied__gt=0).count()

        # Calculate total without discount (what they would have paid)
        total_before_discount = total_spent + total_discount_used

        user_stats.append(
            {
                "user": user,
                "username": user.username,
                "email": user.email,
                "total_orders": total_orders,
                "total_spent": total_spent,
                "total_discount_used": total_discount_used,
                "total_before_discount": total_before_discount,
                "orders_with_discount": orders_with_discount,
                "discount_percentage": (
                    total_discount_used / total_before_discount * 100
                )
                if total_before_discount > 0
                else 0,
                "current_points": user.profile.points,
                "is_vip": user.profile.is_vip,
                "average_order_value": total_spent / total_orders
                if total_orders > 0
                else 0,
            }
        )

    # Sort user stats
    reverse = order_by.startswith("-")
    sort_key = order_by.lstrip("-")
    user_stats.sort(key=lambda x: x.get(sort_key, 0), reverse=reverse)

    # Calculate summary statistics
    summary = {
        "total_customers": len(user_stats),
        "total_orders": sum(u["total_orders"] for u in user_stats),
        "total_revenue": sum(u["total_spent"] for u in user_stats),
        "total_discount_given": sum(u["total_discount_used"] for u in user_stats),
        "vip_customers": sum(1 for u in user_stats if u["is_vip"]),
        "customers_used_discount": sum(
            1 for u in user_stats if u["orders_with_discount"] > 0
        ),
    }

    context = {
        "user_stats": user_stats,
        "summary": summary,
        "search_query": search_query,
        "order_by": order_by,
    }

    return render(request, "user_reports.html", context)


@staff_member_required
def sales_reports(request):
    """Sales Reports - Daily, Monthly, and Annual sales analysis"""

    # Get filter parameters
    report_type = request.GET.get("type", "daily")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # Set default date ranges
    today = timezone.now().date()
    if not start_date:
        if report_type == "daily":
            start_date = today
        elif report_type == "monthly":
            start_date = today.replace(day=1)
        else:  # annual
            start_date = today.replace(month=1, day=1)
    else:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

    if not end_date:
        end_date = today
    else:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    # Base queryset
    orders = Order.objects.filter(
        created_at__date__gte=start_date, created_at__date__lte=end_date
    ).exclude(status="cancelled")

    # Calculate summary
    summary = {
        "total_orders": orders.count(),
        "total_sales": orders.aggregate(Sum("total_amount"))["total_amount__sum"] or 0,
        "total_discount": orders.aggregate(Sum("discount_applied"))[
            "discount_applied__sum"
        ]
        or 0,
        "sales_before_discount": 0,
    }
    summary["sales_before_discount"] = (
        summary["total_sales"] + summary["total_discount"]
    )

    # Time-based breakdown
    if report_type == "daily":
        # Hourly breakdown
        sales_data = []
        for hour in range(24):
            hour_orders = orders.filter(created_at__hour=hour)
            hour_total = (
                hour_orders.aggregate(Sum("total_amount"))["total_amount__sum"] or 0
            )
            hour_discount = (
                hour_orders.aggregate(Sum("discount_applied"))["discount_applied__sum"]
                or 0
            )

            sales_data.append(
                {
                    "period": f"{hour}:00",
                    "orders": hour_orders.count(),
                    "sales": hour_total,
                    "discount": hour_discount,
                    "sales_before_discount": hour_total + hour_discount,
                }
            )

    elif report_type == "monthly":
        # Daily breakdown
        current_date = start_date
        sales_data = []

        while current_date <= end_date:
            day_orders = orders.filter(created_at__date=current_date)
            day_total = (
                day_orders.aggregate(Sum("total_amount"))["total_amount__sum"] or 0
            )
            day_discount = (
                day_orders.aggregate(Sum("discount_applied"))["discount_applied__sum"]
                or 0
            )

            sales_data.append(
                {
                    "period": current_date.strftime("%d/%m/%Y"),
                    "date": current_date,
                    "orders": day_orders.count(),
                    "sales": day_total,
                    "discount": day_discount,
                    "sales_before_discount": day_total + day_discount,
                }
            )
            current_date += timedelta(days=1)

    else:  # annual
        # Monthly breakdown
        sales_data = (
            orders.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(
                orders=Count("id"),
                sales=Sum("total_amount"),
                discount=Sum("discount_applied"),
            )
            .order_by("month")
        )

        # Format the data
        formatted_data = []
        for item in sales_data:
            formatted_data.append(
                {
                    "period": item["month"].strftime("%B %Y"),
                    "date": item["month"],
                    "orders": item["orders"],
                    "sales": item["sales"] or 0,
                    "discount": item["discount"] or 0,
                    "sales_before_discount": (item["sales"] or 0)
                    + (item["discount"] or 0),
                }
            )
        sales_data = formatted_data

    # Discount breakdown
    discount_5_percent = orders.filter(
        discount_applied__gt=0,
        discount_applied__lte=F("total_amount") * 0.06,  # Approximately 5%
    )
    discount_10_percent = orders.filter(
        discount_applied__gt=F("total_amount") * 0.06  # Approximately 10%
    )

    discount_breakdown = {
        "5_percent_count": discount_5_percent.count(),
        "5_percent_amount": discount_5_percent.aggregate(Sum("discount_applied"))[
            "discount_applied__sum"
        ]
        or 0,
        "10_percent_count": discount_10_percent.count(),
        "10_percent_amount": discount_10_percent.aggregate(Sum("discount_applied"))[
            "discount_applied__sum"
        ]
        or 0,
    }

    # Payment method breakdown
    payment_methods = (
        orders.values("payment_method")
        .annotate(count=Count("id"), revenue=Sum("total_amount"))
        .order_by("-count")
    )

    # Chart data
    chart_data = {
        "sales_data": json.dumps(list(sales_data), default=str),
        "payment_methods": json.dumps(list(payment_methods), default=str),
    }

    context = {
        "report_type": report_type,
        "start_date": start_date,
        "end_date": end_date,
        "summary": summary,
        "sales_data": sales_data,
        "discount_breakdown": discount_breakdown,
        "payment_methods": payment_methods,
        "chart_data": chart_data,
    }

    return render(request, "sales_reports.html", context)
