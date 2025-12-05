from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from .models import (
    Category,
    MenuItem,
    NewsFeed,
    CustomerProfile,
    Order,
    OrderItem,
    Reward,
    RewardRedemption,
)
from .admin_models import UserReport, SalesReport


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "order"]
    list_editable = ["order"]
    search_fields = ["name"]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["price", "subtotal"]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "is_available", "created_at"]
    list_filter = ["category", "is_available", "created_at"]
    search_fields = ["name", "description"]
    list_editable = ["is_available"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(NewsFeed)
class NewsFeedAdmin(admin.ModelAdmin):
    list_display = ["title", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["title", "content"]
    list_editable = ["is_active"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "points", "is_vip", "vip_since"]
    list_filter = ["is_vip"]
    search_fields = ["user__username", "user__email"]
    readonly_fields = ["vip_since"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "customer",
        "status",
        "total_amount",
        "points_earned",
        "created_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = ["customer__username", "id"]
    readonly_fields = ["total_amount", "points_earned", "created_at", "updated_at"]
    inlines = [OrderItemInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if change:  # If updating existing order
            obj.calculate_total()


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ["name", "points_required", "tier", "is_active"]
    list_filter = ["tier", "is_active"]
    search_fields = ["name"]
    list_editable = ["is_active"]


@admin.register(RewardRedemption)
class RewardRedemptionAdmin(admin.ModelAdmin):
    list_display = ["customer", "reward", "points_spent", "redeemed_at"]
    list_filter = ["redeemed_at"]
    search_fields = ["customer__username", "reward__name"]
    readonly_fields = ["redeemed_at"]


# ============================================================================
# REPORTS SECTION
# ============================================================================


@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    """Admin interface for User Reports - redirects to user reports view"""

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # Redirect to the user reports page
        return HttpResponseRedirect(reverse("user_reports"))


@admin.register(SalesReport)
class SalesReportAdmin(admin.ModelAdmin):
    """Admin interface for Sales Reports - redirects to sales reports view"""

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # Redirect to the sales reports page
        return HttpResponseRedirect(reverse("sales_reports"))
