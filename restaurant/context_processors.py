# ============================================
# CREATE THIS FILE: restaurant/context_processors.py
# Makes cart available in all templates
# ============================================

from .cart_utils import get_or_create_cart, get_cart_count


def cart_processor(request):
    """
    Add cart information to all template contexts
    """
    try:
        cart = get_or_create_cart(request)
        cart_count = cart.total_items
    except:
        cart = None
        cart_count = 0

    return {
        "cart": cart,
        "cart_count": cart_count,
    }
