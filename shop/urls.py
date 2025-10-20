from django.contrib import admin
from django.urls import path
from store import views as v
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", v.product_list, name="product_list"),
    path("product/<slug:slug>/", v.product_detail, name="product_detail"),
    path("cart/", v.cart_view, name="cart"),

    path("api/cart/add/<int:product_id>/", v.api_add_to_cart, name="api_add_to_cart"),
    path("api/cart/qty/<int:product_id>/", v.api_update_qty, name="api_update_qty"),
    path("api/cart/apply-coupon/", v.api_apply_coupon, name="api_apply_coupon"),
    path("api/checkout/", v.api_checkout, name="api_checkout"),

    path("account/login/", v.login_view, name="login"),
    path("account/register/", v.register_view, name="register"),
    path("account/logout/", v.logout_view, name="logout"),
    path("account/", v.account_dashboard, name="account"),
    path("account/orders/<str:number>/", v.order_detail, name="order_detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)