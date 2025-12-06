# restaurant/cart_utils.py
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Cart, CartItem, MenuItem


def _create_guest_session_if_missing(request):
    if not request.session.session_key:
        request.session.create()


def get_or_create_cart(request):
    """
    Return a cart tied to either request.user (if authenticated) or session (guest).
    Stores stable cart.id in session['cart_id'] to avoid creating duplicate carts.
    Also merges session cart into user cart automatically for logged in users.
    """
    # Authenticated user
    if request.user.is_authenticated:
        # Try to use cart referenced in session first (merge), else get_or_create by user
        cart = None
        session_cart_id = request.session.get("cart_id")
        if session_cart_id:
            try:
                session_cart = Cart.objects.get(id=session_cart_id)
            except Cart.DoesNotExist:
                session_cart = None

            user_cart, created = Cart.objects.get_or_create(user=request.user)
            cart = user_cart

            # If session cart exists and is different, merge items then delete session cart
            if session_cart and session_cart.pk != user_cart.pk:
                for item in session_cart.items.all():
                    add_to_cart(request, item.menu_item.id, item.quantity)
                session_cart.delete()
                # ensure session cart_id points to user's cart
                request.session["cart_id"] = user_cart.id
        else:
            cart, created = Cart.objects.get_or_create(user=request.user)
            request.session["cart_id"] = cart.id

        return cart

    # Guest user
    _create_guest_session_if_missing(request)
    session_key = request.session.session_key

    # Try session cart by session_key or by session cart_id if set
    cart = None
    session_cart_id = request.session.get("cart_id")
    if session_cart_id:
        try:
            cart = Cart.objects.get(id=session_cart_id, session_key=session_key)
        except Cart.DoesNotExist:
            cart = None

    if not cart:
        cart, created = Cart.objects.get_or_create(session_key=session_key)
        request.session["cart_id"] = cart.id

    return cart


@transaction.atomic
def add_to_cart(request, menu_item_id, quantity=1, replace_quantity=False):
    """
    Add an item to cart.
    - If replace_quantity=True: set item quantity to `quantity`.
    - Else: increment existing quantity by `quantity`.
    Returns the CartItem.
    """
    cart = get_or_create_cart(request)
    menu_item = get_object_or_404(MenuItem, id=menu_item_id, is_available=True)

    cart_item, created = CartItem.objects.select_for_update().get_or_create(
        cart=cart, menu_item=menu_item, defaults={"quantity": 0}
    )

    if replace_quantity:
        cart_item.quantity = max(0, int(quantity))
    else:
        cart_item.quantity += int(quantity)

    if cart_item.quantity <= 0:
        cart_item.delete()
        return None

    cart_item.save()
    # keep session cart_count up to date
    request.session["cart_count"] = cart.total_items
    return cart_item


@transaction.atomic
def update_cart_item(request, menu_item_id, quantity):
    """
    Set absolute quantity of a cart item. If quantity <= 0 the item is removed.
    Returns the updated CartItem or None if removed.
    """
    cart = get_or_create_cart(request)
    try:
        cart_item = CartItem.objects.select_for_update().get(
            cart=cart, menu_item_id=menu_item_id
        )
    except CartItem.DoesNotExist:
        return None

    quantity = int(quantity)
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
        cart_item = None

    request.session["cart_count"] = cart.total_items
    return cart_item


@transaction.atomic
def remove_from_cart(request, menu_item_id):
    """
    Remove a cart item entirely.
    """
    cart = get_or_create_cart(request)
    try:
        ci = CartItem.objects.get(cart=cart, menu_item_id=menu_item_id)
        ci.delete()
    except CartItem.DoesNotExist:
        pass

    request.session["cart_count"] = cart.total_items
    return True


def clear_cart(request):
    """
    Remove all items from the cart.
    For guests, delete the cart itself and pop session cart_id to avoid duplicates.
    """
    cart = get_or_create_cart(request)
    # Delete items
    cart.items.all().delete()

    if not request.user.is_authenticated:
        # Delete cart row (so a new clean cart will be created next time)
        cart.delete()
        request.session.pop("cart_id", None)

    request.session["cart_count"] = 0
    return True


def get_cart_count(request):
    try:
        cart = get_or_create_cart(request)
        return cart.total_items
    except Exception:
        return 0
