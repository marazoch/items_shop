from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils.crypto import get_random_string

from .models import Product, Category, Cart, CartItem, Order
from .forms import RegistrationForm, LoginForm
from .services import get_or_create_cart, add_to_cart, update_item_qty, apply_coupon, checkout

def ensure_session(request):
    """Гарантирует, что у запроса есть session_key"""
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key

def product_list(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    return render(request, "store/product_list.html", {"products": products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "store/product_detail.html", {"product": product})

def cart_view(request):
    session_key = ensure_session(request)
    cart = get_or_create_cart(session_key)
    return render(request, "store/cart.html", {"cart": cart})

@require_http_methods(["POST"])
def api_add_to_cart(request, product_id):
    session_key = ensure_session(request)
    cart = get_or_create_cart(session_key)
    qty = int(request.POST.get("qty", 1))
    try:
        item = add_to_cart(cart, product_id, qty)
        return JsonResponse({"ok": True, "qty": item.qty})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

@require_http_methods(["POST"])
def api_update_qty(request, product_id):
    session_key = ensure_session(request)
    cart = get_or_create_cart(session_key)
    qty = int(request.POST.get("qty", 1))
    try:
        update_item_qty(cart, product_id, qty)
        return JsonResponse({"ok": True})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

@require_http_methods(["POST"])
def api_apply_coupon(request):
    session_key = ensure_session(request)
    cart = get_or_create_cart(session_key)
    code = (request.POST.get("code") or "").strip()
    try:
        coupon = apply_coupon(cart, code)
        return JsonResponse({"ok": True, "coupon": coupon.code})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

@require_http_methods(["POST"])
def api_checkout(request):
    """Чекаут с учётом авторизации"""
    session_key = ensure_session(request)
    cart = get_or_create_cart(session_key)

    # email: из формы или из профиля
    email = (request.POST.get("email", "") or "").strip()
    if not email and request.user.is_authenticated and request.user.email:
        email = request.user.email.strip()

    if not email:
        return HttpResponseBadRequest("email required")

    if request.user.is_authenticated and not request.user.email and email:
        try:
            request.user.email = email
            request.user.save(update_fields=["email"])
        except Exception:
            pass

    try:
        order = checkout(cart, email, user=request.user)
        return JsonResponse({"ok": True, "order": order.number, "total": float(order.total)})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

def register_view(request):
    if request.user.is_authenticated:
        return redirect(request.GET.get("next") or "account")
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно! Добро пожаловать 👋")
            return redirect(request.GET.get("next") or "account")
    else:
        form = RegistrationForm()
    return render(request, "store/auth_register.html", {"form": form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect(request.GET.get("next") or "account")
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Вы успешно вошли в аккаунт.")
            return redirect(request.GET.get("next") or "account")
    else:
        form = LoginForm()
    return render(request, "store/auth_login.html", {"form": form})

def logout_view(request):
    logout(request)
    messages.success(request, "Вы вышли из аккаунта.")
    return redirect("product_list")

@login_required
def account_dashboard(request):
    """Показываем заказы пользователя или по совпадающему email"""
    orders = Order.objects.filter(Q(user=request.user) | Q(email=request.user.email)).order_by("-created_at")
    return render(request, "store/account_dashboard.html", {"orders": orders})

@login_required
def order_detail(request, number):
    order = get_object_or_404(Order, number=number)
    if not (order.user == request.user or order.email == request.user.email):
        return redirect("account")
    items = order.items.all()
    return render(request, "store/order_detail.html", {"order": order, "items": items})
