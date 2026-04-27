from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register, name="accounts_register"),
    path("login/", views.AccountsLoginView.as_view(), name="accounts_login"),
    path("logout/", views.AccountsLogoutView.as_view(), name="accounts_logout"),
    path("profile/", views.profile, name="accounts_profile"),
]
