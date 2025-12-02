from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("feeds/", views.feeds, name="feeds"),
    path("menu/", views.menu, name="menu"),
    path("order/", views.place_order, name="place_order"),
    path("order-history/", views.order_history, name="order_history"),
    path("redeem/<int:reward_id>/", views.redeem_reward, name="redeem_reward"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
]
