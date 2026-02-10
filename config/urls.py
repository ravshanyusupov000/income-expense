from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("finance.urls")),

    # path("accounts/register/", register_view, name="register"),
    path("accounts/", include("django.contrib.auth.urls")),

    path("i18n/", include("django.conf.urls.i18n")),
]

