from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.products, name='products'),
    path('products/detail/<slug:slug>/', views.detail, name='detail'),
    path('categories/<slug:slug>/', views.category, name='category')
]