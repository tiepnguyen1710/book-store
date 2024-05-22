from django.utils.deprecation import MiddlewareMixin
from .models import Cart

class CartMiddleware(MiddlewareMixin):
    def process_request(self, request):
        cart_id = request.COOKIES.get('cart_id')
        if not cart_id:
            cart = Cart.objects.create()
            request.cart_id = cart.id
        else:
            request.cart_id = cart_id

    def process_response(self, request, response):
        if hasattr(request, 'cart_id'):
            response.set_cookie('cart_id', request.cart_id, max_age=3600*24*7)
        return response