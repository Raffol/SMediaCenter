from django.urls import path

from accounts import views_auth as v

urlpatterns = [
    path("csrf/", v.csrf),
    path("login/", v.login_view),
    path("logout/", v.logout_view),
    path("me/", v.me),
    path("change-password/", v.change_password),
]
