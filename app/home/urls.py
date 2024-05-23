from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.products, name='products'),
    path('products/detail/<slug:slug>/', views.detail, name='detail'),
    path('categories/<slug:slug>/', views.category, name='category'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/delete/<int:product_id>/', views.delete_from_cart, name='cart_delete'),
    path('cart/update/<int:product_id>/<int:quantity>/', views.update_item, name='update_item'),
    path('cart/', views.cart_index, name='cart_index'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/order', views.checkout_order, name='checkout_order'),
    path('user/register', views.register, name='register'),
    path('user/registerPost', views.registerPost, name='register'),
    path('user/login', views.login, name='login'),
    path('user/loginPost', views.loginPost, name='loginPost'),
    path('user/logout', views.logout, name='logout'),
    path('search', views.search, name='search'),
]