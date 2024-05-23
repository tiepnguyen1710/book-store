from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.contrib.auth.models import Group, Permission

class Product(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey('ProductCategory', on_delete=models.CASCADE, null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    thumbnail = models.URLField(max_length=200)
    featured = models.BooleanField(default=False)  
    slug = models.SlugField(unique=True, blank=True)
    deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class ProductCategory(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = models.TextField()
    deleted = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Cart(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    #user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    cart = models.ForeignKey('Cart', on_delete=models.SET_NULL, null=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order {self.id} by {self.full_name}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.FloatField()
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.quantity} x {self.product.title}'

class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    token_user = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.URLField(blank=True, null=True)
    groups = models.ManyToManyField(Group, related_name='custom_user_groups', blank=True, verbose_name='Groups')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions', blank=True, verbose_name='User Permissions')
    

    def __str__(self):
        return self.full_name
    
