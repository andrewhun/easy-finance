from . import views
from django.urls import path

urlpatterns = [
path("", views.index, name ="index"),
path("auto_values/", views.auto_values, name = "auto_values"),
path("manual_values/", views.manual_values, name = "manual_values"),
path("edit_auto/", views.edit_auto, name = "edit_auto"),
path("edit_hist/", views.edit_hist, name = "edit_hist"),
path("delete_auto/", views.delete_auto, name = "delete_auto"),
path("delete_hist/", views.delete_hist, name = "delete_hist"),
path("delete_all_auto/", views.delete_all_auto, name = "delete_all_auto"),
path("delete_all_hist/", views.delete_all_hist, name = "delete_all_hist"),
path("edit_balance/", views.edit_balance, name = "edit_balance"),
path("stocks/", views.stocks, name = "stocks"),
path("buy/", views.buy, name = "buy"),
path("history/", views.history, name = "history"),
path("login/", views.login_view, name = "login"),
path("logout/", views.logout_view, name = "logout"),
path("quote/", views.quote, name = "quote"),
path("register/", views.register, name = "register"),
path("sell/", views.sell, name = "sell"),
path("change_pw/", views.change_pw, name = "change_pw"),]