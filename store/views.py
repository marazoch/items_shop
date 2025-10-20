from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import Product, Category
from .services import get_or_create_cart, add_to_cart, update_item_qty, apply_coupon, checkout
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect
from django.db.models import Q
from .forms import RegistrationForm

def ensure_session(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key

def product_list(request):
    ctx = {
        "categories": Category.objects.all(),
        "products": Product.objects.filter(is_active=True),
    }
    return render(request, "store/product_list.html", ctx)

def cart_view(request):
    session_key = ensure_session(request)
    cart = get_or_create_cart(session_key)
    return render(request, "store/cart.html", {"cart": cart})

@require_http_methods(["POST"])
def api_add_to_cart(request, product_id):
    session_key = ensure_session(request)
    cart = get_or_create_cart(session_key)
    qty = int(request.POST.get("qty", "1"))
    try:
        item = add_to_cart(cart, product_id, qty)
        return JsonResponse({"ok": True, "product": item.product.name, "qty": item.qty})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

@require_http_methods(["POST"])
def api_update_qty(request, product_id):
    session_key = ensure_session(request)
    cart = get_or_create_cart(session_key)
    qty = int(request.POST.get("qty", "1"))
    try:
        update_item_qty(cart, product_id, qty)
        return JsonResponse({"ok": True})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

@require_http_methods(["POST"])
def api_apply_coupon(request):
    session_key = ensure_session(request)
    cart = get_or_create_cart(session_key)
    code = request.POST.get("code", "").strip()
    if not code:
        return HttpResponseBadRequest("code required")
    try:
        c = apply_coupon(cart, code)
        return JsonResponse({"ok": True, "coupon": c.code})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

@require_http_methods(["POST"])
def api_checkout(request):
    session_key = ensure_session(request)
    cart = get_or_create_cart(session_key)
    email = request.POST.get("email", "").strip()
    if not email:
        return HttpResponseBadRequest("email required")
    try:
        order = checkout(cart, email, user=request.user)  # ← НОВОЕ
        return JsonResponse({"ok": True, "order": order.number, "total": float(order.total)})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "store/product_detail.html", {"product": product})

def register_view(request):
    if request.user.is_authenticated:
        return redirect("account")
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно! Добро пожаловать 👋")
            return redirect("account")
    else:
        form = RegistrationForm()
    return render(request, "store/auth_register.html", {"form": form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect("account")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Вы успешно вошли в аккаунт.")
            return redirect("account")
    else:
        form = AuthenticationForm(request)
    return render(request, "store/auth_login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("product_list")

@login_required
def account_dashboard(request):
    """
    Показываем заказы пользователя (привязанные по FK) + заказы на его email (если такие есть),
    чтобы покрыть случаи оформления без авторизации.
    """
    from .models import Order
    qs = Order.objects.filter(Q(user=request.user) | Q(email=request.user.email)).order_by("-created_at")
    return render(request, "store/account_dashboard.html", {"orders": qs})

@login_required
def order_detail(request, number):
    from .models import Order, OrderItem
    order = get_object_or_404(Order, number=number)
    # доступ — если это его заказ (по user) или совпадает email
    if not (order.user == request.user or order.email == request.user.email):
        return redirect("account")
    items = order.items.all()
    return render(request, "store/order_detail.html", {"order": order, "items": items})