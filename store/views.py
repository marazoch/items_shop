from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import Product, Category
from .services import get_or_create_cart, add_to_cart, update_item_qty, apply_coupon, checkout

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
        order = checkout(cart, email)
        return JsonResponse({"ok": True, "order": order.number, "total": float(order.total)})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "store/product_detail.html", {"product": product})
