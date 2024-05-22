from django.db import models
from django.utils.text import slugify

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