from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("feeds/", views.feeds, name="feeds"),
    path("menu/", views.menu, name="menu"),
    path("order/", views.place_order, name="place_order"),
    path("checkout/", views.checkout, name="checkout"),
    path("order-history/", views.order_history, name="order_history"),
    # Redemption URLs
    path("redeem/discount/", views.redeem_discount, name="redeem_discount"),
    path("redeem/reward/", views.redeem_reward, name="redeem_reward"),
    path(
        "redeem/<int:reward_id>/", views.redeem_reward, name="redeem_reward"
    ),  # Keep for backward compatibility
    # Auth URLs
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("feeds/<int:news_id>/", views.feed_detail, name="feed_detail"),
    path("admin-reports/", views.admin_reports, name="admin_reports"),
    path("reports/users/", views.user_reports, name="user_reports"),
    path("reports/sales/", views.sales_reports, name="sales_reports"),
    path("reports/", views.reports_menu, name="reports_menu"),
]
