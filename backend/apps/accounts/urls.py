from django.urls import path

from .views import SendCodeView, LoginCodeView, MeView

urlpatterns = [
    path("auth/send-code/", SendCodeView.as_view(), name="send-code"),
    path("auth/login-code/", LoginCodeView.as_view(), name="login-code"),
    path("auth/me/", MeView.as_view(), name="me"),
]
