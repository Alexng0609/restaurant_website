# ============================================
# CREATE THIS FILE: restaurant/cart_utils.py
# Cart helper functions
# ============================================

from .models import Cart, CartItem, MenuItem
from django.shortcuts import get_object_or_404


def get_or_create_cart(request):
    """
    Get or create cart for current user/session
    """
    if request.user.is_authenticated:
        # For logged-in users
        cart, created = Cart.objects.get_or_create(user=request.user)

        # If user has session cart, merge it
        if request.session.session_key:
            try:
                session_cart = Cart.objects.get(session_key=request.session.session_key)
                if session_cart.pk != cart.pk:
                    # Merge session cart into user cart
                    for item in session_cart.items.all():
                        add_to_cart(request, item.menu_item.id, item.quantity)
                    session_cart.delete()
            except Cart.DoesNotExist:
                pass
    else:
        # For anonymous users, use session
        if not request.session.session_key:
            request.session.create()

        cart, created = Cart.objects.get_or_create(
            session_key=request.session.session_key
        )

    return cart


def add_to_cart(request, menu_item_id, quantity=1):
    """
    Add item to cart or update quantity
    """
    cart = get_or_create_cart(request)
    menu_item = get_object_or_404(MenuItem, id=menu_item_id, is_available=True)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, menu_item=menu_item, defaults={"quantity": quantity}
    )

    if not created:
        # Item already in cart, update quantity
        cart_item.quantity += quantity
        cart_item.save()

    return cart_item


def update_cart_item(request, menu_item_id, quantity):
    """
    Update cart item quantity
    """
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, cart=cart, menu_item_id=menu_item_id)

    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()

    return cart_item if quantity > 0 else None


def remove_from_cart(request, menu_item_id):
    """
    Remove item from cart
    """
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, cart=cart, menu_item_id=menu_item_id)
    cart_item.delete()
    return True


def get_cart_count(request):
    """
    Get total number of items in cart
    """
    try:
        cart = get_or_create_cart(request)
        return cart.total_items
    except:
        return 0
