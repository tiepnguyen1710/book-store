from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect
from django.urls import reverse
from decimal import Decimal
from .models import Product, ProductCategory, Cart, CartItem, Order, OrderItem

# Create your views here.

def index(request):
    return render(request, 'pages/home/index.html')

def products(request):
    products = Product.objects.filter(deleted=False)
    #print(products)
    print(type(products))

    for product in products:
        product.priceNew = product.price * (1 - product.discount_percentage / 100)
        product.priceNew = round(product.priceNew, 0)
        product.price = round(product.price, 0)
        product.discount_percentage = round(product.discount_percentage, 0)

    # Render template với các sản phẩm
    context = {
        'pageTitle': "Danh sách sản phẩm",
        'products': products
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
            "product": product
        }
        return render(request, 'pages/products/detail.html', context)
    except Product.DoesNotExist:
        return redirect("/")
    
def category(request, slug):
    category = get_object_or_404(ProductCategory, slug=slug)
    products = Product.objects.filter(category=category, deleted=False)

    for product in products:
        product.priceNew = product.price * (1 - product.discount_percentage / 100)
        product.priceNew = round(product.priceNew, 0)
        product.price = round(product.price, 0)
        product.discount_percentage = round(product.discount_percentage, 0)
    
    context = {
        'category': category,
        'products': products,
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
        'page_title': 'Giỏ hàng',
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
            item.price_new = (product.price * (100 - product.discount_percentage) / 100).quantize(Decimal('0.01'))
            item.total_price = item.price_new * item.quantity
            order.total_price += item.total_price

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