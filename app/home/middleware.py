from django.utils.deprecation import MiddlewareMixin

from .models import Cart, CustomUser

class CartMiddleware(MiddlewareMixin):
    def process_request(self, request):
        cart_id = request.COOKIES.get('cart_id')
        if not cart_id:
            cart = Cart.objects.create()
            request.cart_id = cart.id
        else:
            request.cart_id = cart_id
    # def process_request(self, request):
    #     if request.user.is_authenticated:
    #         # Người dùng đã đăng nhập
    #         #cart, created = Cart.objects.get_or_create(user=request.user)
    #         print("")
    #         #request.cart_id = cart.id
    #         #response.set_cookie('card_id', cart.id)
    #     else:
    #         # Người dùng chưa đăng nhập
    #         cart_id = request.COOKIES.get('cart_id')
    #         if not cart_id:
    #             cart = Cart.objects.create()
    #             request.cart_id = cart.id
    #         else:
    #             request.cart_id = cart_id

    def process_response(self, request, response):
        if hasattr(request, 'cart_id'):
            response.set_cookie('cart_id', request.cart_id, max_age=3600*24*7)
        return response
    
class UserInfoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'token_user' in request.COOKIES :
            try:
                user = CustomUser.objects.get(token_user=request.COOKIES['token_user'])
                request.user = user
            except CustomUser.DoesNotExist:
                pass
        else:
            request.user = None  # Không có token, nên không có user

        response = self.get_response(request)
        return response