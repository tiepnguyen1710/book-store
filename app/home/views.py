from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout as django_logout
from django.contrib.auth import authenticate, login as django_login
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from decimal import Decimal
from .models import Product, ProductCategory, Cart, CartItem, Order, OrderItem, CustomUser
from home.helper.pagination_helper import get_pagination, get_pagination_home

# Create your views here.

def index(request):
    products = Product.objects.filter(deleted=False, featured=True)

    for product in products:
        product.priceNew = product.price * (1 - product.discount_percentage / 100)
        product.priceNew = round(product.priceNew, 0)
        product.price = round(product.price, 0)
        product.discount_percentage = round(product.discount_percentage, 0)
    context = {
        'pageTitle': "Trang chủ",
        'products' : products
    }
    return render(request, 'pages/home/index.html', context)

def products(request):
    products = Product.objects.filter(deleted=False)
    #print(products)
    print(type(products))
    # Xử lý sắp xếp
    sort_key = request.GET.get('sortKey', 'price')
    sort_value = request.GET.get('sortValue', 'desc')
    if sort_value == 'asc':
        order_by = sort_key
    else:
        order_by = f'-{sort_key}'

    products = products.order_by(order_by)

    count_records = products.count()

    # Sử dụng helper để lấy thông tin phân trang
    pagination = get_pagination_home(request, count_records)

    # Cập nhật queryset để chỉ lấy các sản phẩm cho trang hiện tại
    products = products[pagination['skip']:pagination['skip'] + pagination['limit_items']]


    for product in products:
        product.priceNew = product.price * (1 - product.discount_percentage / 100)
        product.priceNew = round(product.priceNew, 0)
        product.price = round(product.price, 0)
        product.discount_percentage = round(product.discount_percentage, 0)
    
    page_numbers = range(1, pagination['total_page'] + 1)

    # Render template với các sản phẩm
    context = {
        'pageTitle': "Danh sách sản phẩm",
        'products': products,
        'object_pagination': pagination,
        'page_numbers': page_numbers,
        'sort_key': sort_key,
        'sort_value': sort_value
    }
    return render(request, 'pages/products/index.html', context)

def detail(request, slug):
    try:
        product = Product.objects.get(slug=slug, deleted=False)
        product.priceNew = round(product.price * (100 - product.discount_percentage) / 100)
        product.price = round(product.price, 0)
        product.discount_percentage = round(product.discount_percentage, 0)

        context = {
            "pageTitle": "Chi tiết sản phẩm", 
            "product": product,
        }
        return render(request, 'pages/products/detail.html', context)
    except Product.DoesNotExist:
        return redirect("/")
    
def category(request, slug):
    category = get_object_or_404(ProductCategory, slug=slug)
    products = Product.objects.filter(category=category, deleted=False)

    # Xử lý sắp xếp
    sort_key = request.GET.get('sortKey', 'price')
    sort_value = request.GET.get('sortValue', 'desc')
    if sort_value == 'asc':
        order_by = sort_key
    else:
        order_by = f'-{sort_key}'

    products = products.order_by(order_by)

    count_records = products.count()

    # Sử dụng helper để lấy thông tin phân trang
    pagination = get_pagination(request, count_records)

    # Cập nhật queryset để chỉ lấy các sản phẩm cho trang hiện tại
    products = products[pagination['skip']:pagination['skip'] + pagination['limit_items']]

    for product in products:
        product.priceNew = product.price * (1 - product.discount_percentage / 100)
        product.priceNew = round(product.priceNew, 0)
        product.price = round(product.price, 0)
        product.discount_percentage = round(product.discount_percentage, 0)

    page_numbers = range(1, pagination['total_page'] + 1)
    
    context = {
        "pageTitle": "Danh mục",
        'category': category,
        'products': products,
        'object_pagination': pagination,
        'page_numbers': page_numbers,
        'sort_key': sort_key,
        'sort_value': sort_value
    }
    return render(request, 'pages/categories/index.html', context)

@require_POST
def add_to_cart(request, product_id):
    cart_id = getattr(request, 'cart_id', None)
    cart = get_object_or_404(Cart, id=cart_id)

    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    # Kiểm tra xem sản phẩm đã tồn tại trong giỏ hàng chưa
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()
    
    # Set the cart cookie
    response = redirect(f'http://localhost:8000/products/detail/{product.slug}')
    response.set_cookie('cart_id', cart_id, max_age=3600*24*7)  

    return response

def cart_index(request):
    cart_id = getattr(request, 'cart_id', None)
    cart = get_object_or_404(Cart, id=cart_id)

    total_price = 0
    cart_items = []

    # Lấy tất cả các CartItem liên quan đến giỏ hàng này
    items = CartItem.objects.filter(cart=cart)

    for item in items:
        product = item.product
        # Tính giá mới sau khi giảm giá và tổng giá cho sản phẩm
        price_new = (product.price * (100 - product.discount_percentage) / 100)
        price_new = round(price_new, 0)
        total_item_price = (price_new * item.quantity)
        total_item_price = round(total_item_price, 0)
        total_price += total_item_price
        total_price = round(total_price, 0)

        cart_items.append({
            'product': product,
            'quantity': item.quantity,
            'price_new': price_new,
            'total_item_price': total_item_price,
        })

    return render(request, 'pages/cart/index.html', {
        'pageTitle': 'Giỏ hàng',
        'cart_items': cart_items,
        'total_price': total_price,
    })

def delete_from_cart(request, product_id):
    cart_id = request.COOKIES.get('cart_id')
    cart = get_object_or_404(Cart, id=cart_id)
    cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
    cart_item.delete()
    return redirect('cart_index')

def update_item(request, product_id, quantity):
    cart_id = request.COOKIES.get('cart_id')
    cart = get_object_or_404(Cart, id=cart_id)

    product = get_object_or_404(Product, id=product_id)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)

    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
        request.session['success'] = "Cập nhật sản phẩm thành công!"
    else:
        cart_item.delete()
        request.session['success'] = "Xóa sản phẩm khỏi giỏ hàng thành công!"

    return redirect(request.META.get('HTTP_REFERER', 'cart_index'))

def checkout(request):
    cart_id = getattr(request, 'cart_id', None)
    cart = get_object_or_404(Cart, id=cart_id)

    total_price = 0
    cart_items = []

    # Lấy tất cả các CartItem liên quan đến giỏ hàng này
    items = CartItem.objects.filter(cart=cart)

    for item in items:
        product = item.product
        # Tính giá mới sau khi giảm giá và tổng giá cho sản phẩm
        price_new = (product.price * (100 - product.discount_percentage) / 100)
        price_new = round(price_new, 0)
        total_item_price = (price_new * item.quantity)
        total_item_price = round(total_item_price, 0)
        total_price += total_item_price
        total_price = round(total_price, 0)

        cart_items.append({
            'product': product,
            'quantity': item.quantity,
            'price_new': price_new,
            'total_item_price': total_item_price,
        })

    return render(request, 'pages/checkout/index.html', {
        'page_title': 'Giỏ hàng',
        'cart_items': cart_items,
        'total_price': total_price,
    })

def checkout_order(request):
    if request.method == 'POST':
        full_name = request.POST.get('fullName')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        cart_id = request.COOKIES.get('cart_id')
        cart = get_object_or_404(Cart, id=cart_id)

        order = Order.objects.create(
            cart=cart,
            full_name=full_name,
            phone=phone,
            address=address
        )

        cart_items = CartItem.objects.filter(cart=cart)
        for item in cart_items:
            product = item.product
            OrderItem.objects.create(
                order=order,
                product=product,
                price=product.price,
                discount_percentage=product.discount_percentage,
                quantity=item.quantity
            )

        # Clear the cart
        cart_items.delete()

        # Calculate order total price and retrieve order items
        order.total_price = Decimal('0.00')
        order_items = []
        #items = CartItem.objects.filter(cart=cart)

        for item in OrderItem.objects.filter(order=order):
            product = item.product
            item.price_new = (product.price * (100 - product.discount_percentage) / 100)
            item.price_new = round(item.price_new, 0)
            item.total_price = item.price_new * item.quantity
            item.total_price = round(item.total_price, 0)
            order.total_price += item.total_price
            order.total_price = round(order.total_price, 0)

            order_items.append({
                'product': product,
                'quantity': item.quantity,
                'price_new': item.price_new,
                'total_item_price': item.total_price,
            })

        return render(request, 'pages/checkout/success.html', {
            'order': order,
            'order_items': order_items,
            'total_price': order.total_price,
        })

    return redirect('cart_index')

# def checkout_success(request, order_id):
#     order = get_object_or_404(Order, id=order_id)
#     order.total_price = Decimal('0.00')
    
#     for item in order.orderitem_set.all():
#         product = item.product
#         item.price_new = (product.price * (100 - product.discount_percentage) / 100).quantize(Decimal('0.01'))
#         item.total_price = item.price_new * item.quantity
#         order.total_price += item.total_price

#     return render(request, 'pages/checkout/success.html', {'order': order})

def register(request):
    return render(request, 'pages/user/register.html')

def generate_random_string(length):
    import random
    import string
    characters = string.ascii_letters + string.digits
    result = ''.join(random.choice(characters) for _ in range(length))
    return result

def generate_username(email):
    # Lấy phần trước dấu '@' trong email
    base_username = email.split('@')[0]
    username = base_username
    counter = 1

    # Đảm bảo username là duy nhất
    while CustomUser.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1

    return username

def registerPost(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        full_name = request.POST.get('fullName')
        password = request.POST.get('password')

        # Kiểm tra xem email đã tồn tại chưa
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email đã tồn tại!")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        username = generate_username(email)

        # Tạo người dùng mới
        token_user = generate_random_string(30)
        #hashed_password = hashlib.md5(password.encode()).hexdigest()

        user = CustomUser.objects.create(
            full_name=full_name,
            email=email,
            username=username,
            #password=hashed_password,
            password=password,
            token_user=token_user
        )

        # Đặt cookie token_user
        response = redirect('/')
        response.set_cookie('token_user', token_user)

        return response

    return render(request, 'register.html')

def login(request):
    return render(request, 'pages/user/login.html')

def loginPost(request):
    cart_id = getattr(request, 'cart_id', None)
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = CustomUser.objects.get(email=email)
            if user.password == password:
                # Xử lý đăng nhập thành công
                django_login(request, user)
                messages.success(request, 'Đăng nhập')
                response = redirect('/')
                response.set_cookie('token_user', user.token_user)
                # cart = Cart.objects.get(id=cart_id)
                # cart.user = user
                # cart.save()
                return response
                # if cart_id:
                #     try:
                #         cart = Cart.objects.get(id=cart_id)
                #         cart.user = user
                #         cart.save()
                #     except Cart.DoesNotExist:
                #         cart = Cart.objects.create(user=user)
                # else:
                # cart = Cart.objects.filter(user=user).first()
                # response.set_cookie('cart_id', cart.id, max_age=3600*24*7)

                #return response
            else:
                # Xử lý sai mật khẩu
                messages.error(request, 'Sai mật khẩu!')
                return redirect('login')
        except CustomUser.DoesNotExist:
            # Xử lý email không tồn tại
            messages.error(request, 'Email không tồn tại!')
            return redirect('login')
        
        

    return redirect('login')


def logout(request):
    django_logout(request)
    response = redirect('/')
    #response.delete_cookie('cart_id')
    response.delete_cookie('token_user')
    return response

def search(request):
    keyword = request.GET.get('keyword', '')

    if keyword:
        products = Product.objects.filter(
            title__icontains=keyword,
            deleted=False,
        )
        for item in products:
            item.priceNew = round(item.price * (100 - item.discount_percentage) / 100)
    else:
        products = []

    context = {
        'pageTitle': 'Kết quả tìm kiếm',
        'keyword': keyword,
        'products': products
    }

    return render(request, "pages/search/index.html", context)