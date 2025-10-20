from django.db import transaction
from django.utils.crypto import get_random_string
from .models import Cart, CartItem, Product, Coupon, Order, OrderItem

def get_or_create_cart(session_key: str) -> Cart:
    cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart

def add_to_cart(cart: Cart, product_id: int, qty: int = 1):
    product = Product.objects.get(pk=product_id, is_active=True)
    if qty < 1:
        qty = 1
    if product.quantity < qty:
        raise ValueError("Недостаточно товара на складе")

    item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'qty': qty})
    if not created:
        new_qty = item.qty + qty
        if product.quantity < new_qty:
            raise ValueError("Недостаточно товара на складе")
        item.qty = new_qty
        item.save()
    return item

def update_item_qty(cart: Cart, product_id: int, qty: int):
    item = CartItem.objects.get(cart=cart, product_id=product_id)
    if qty <= 0:
        item.delete()
    else:
        product = item.product
        if product.quantity < qty:
            raise ValueError("Недостаточно товара на складе")
        item.qty = qty
        item.save()
    return True

def apply_coupon(cart: Cart, code: str):
    coupon = Coupon.objects.get(code__iexact=code)
    if not coupon.is_valid():
        raise ValueError("Промокод недействителен")
    cart.coupon = coupon
    cart.save()
    return coupon

@transaction.atomic
def checkout(cart: Cart, email: str) -> Order:
    for it in cart.items.select_related('product'):
        if it.product.quantity < it.qty:
            raise ValueError(f"Товара '{it.product.name}' недостаточно на складе")

    order = Order.objects.create(
        number=get_random_string(10).upper(),
        email=email,
        total=cart.total()
    )

    for it in cart.items.select_related('product'):
        OrderItem.objects.create(
            order=order, product_name=it.product.name, price=it.product.price, qty=it.qty
        )
        it.product.quantity -= it.qty
        it.product.save()

    cart.items.all().delete()
    cart.coupon = None
    cart.save(update_fields=["coupon", "updated_at"])
    return order
