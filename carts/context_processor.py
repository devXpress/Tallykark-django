from .models import CartItem, Cart
from .views import _cart_id

def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    
    try:
        cart = Cart.objects.filter(cart_id=_cart_id(request))
        if request.user.is_authenticated:
            cart_items = CartItem.objects.all().filter(user=request.user)
        else:
            cart_items = CartItem.objects.filter(cart=cart[:1])
        for cart_item in cart_items:
            cart_count += cart_item.quantity
    except Cart.DoesNotExist:
        cart_count = 0
    
    return dict(cart_count=cart_count)