from django.contrib import admin
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
