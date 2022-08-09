from django.urls import path
from .views import PasswordTokenCheckAPI, RegisterView, VerifyEmail, LoginAPIView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("verify-email/", VerifyEmail.as_view(), name="email-verification"),
    path("token/refresh/", TokenRefreshView.as_view(), name="tokenrefresh"),
    path(
        "password-reset/<uid64>/token/",
        PasswordTokenCheckAPI.as_view(),
        name="password-reset-confirm",
    ),
]
