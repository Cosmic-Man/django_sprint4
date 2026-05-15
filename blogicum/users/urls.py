from django.urls import path
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordChangeDoneView,
)
from . import views

app_name = "users"

urlpatterns = [
    path("registration/",
         views.RegistrationView.as_view(), name="registration"),
    path("profile/<str:username>/",
         views.ProfileView.as_view(), name="profile"),
    path("login/",
         LoginView.as_view(template_name="users/login.html"), name="login"),
    path(
        "logout/",
        LogoutView.
        as_view(template_name="users/logged_out.html"),
        name="logout",
    ),
    path(
        "password_change/",
        PasswordChangeView.
        as_view(template_name="users/password_change_form.html"),
        name="password_change",
    ),
    path(
        "password_change/done/",
        PasswordChangeDoneView.
        as_view(template_name="users/password_change_done.html"),
        name="password_change_done",
    ),
]
