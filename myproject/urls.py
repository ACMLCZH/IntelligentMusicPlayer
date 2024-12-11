from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import redirect

urlpatterns = [
    re_path(r"^$", lambda request: redirect("/index")),
    path("admin/", admin.site.urls),
    path("", include("myapp.urls")),
]
