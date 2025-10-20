from django.contrib import admin
from django.urls import path
from store import views as v
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

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

    path("account/password-reset/", auth_views.PasswordResetView.as_view(
        template_name="store/password_reset_form.html",
        email_template_name="store/password_reset_email.txt",
        subject_template_name="store/password_reset_subject.txt",
        success_url="/account/password-reset/done/"
    ), name="password_reset"),
    path("account/password-reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="store/password_reset_done.html"
    ), name="password_reset_done"),
    path("account/reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="store/password_reset_confirm.html",
        success_url="/account/reset/done/"
    ), name="password_reset_confirm"),
    path("account/reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="store/password_reset_complete.html"
    ), name="password_reset_complete"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)