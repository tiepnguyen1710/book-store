from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, ProductCategory

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