from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    def __str__(self):
        return self.name

class Coupon(models.Model):
    code = models.CharField(max_length=32, unique=True)
    percent_off = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    def is_valid(self):
        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_to

    def __str__(self):
        return f"{self.code} (-{self.percent_off}%)"

class Cart(models.Model):
    session_key = models.CharField(max_length=40, db_index=True, unique=True)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def subtotal(self):
        return sum(item.subtotal() for item in self.items.all())

    def discount_amount(self):
        if self.coupon and self.coupon.is_valid():
            return self.subtotal() * self.coupon.percent_off / 100
        return 0

    def total(self):
        return self.subtotal() - self.discount_amount()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ('cart', 'product')

    def subtotal(self):
        return self.product.price * self.qty

class Order(models.Model):
    number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    user = models.ForeignKey(  # ← НОВОЕ
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='orders'
    )
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='new', choices=[('new','New'),('paid','Paid'),('cancelled',
                                                                                                    'Cancelled')])

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    qty = models.PositiveIntegerField()
