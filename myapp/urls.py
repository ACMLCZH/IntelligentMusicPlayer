from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('login/', views.login, name='login'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('sign_in_sign_up_reset_request', views.backend_login_process, name='sign_in_sign_up_reset_request')
   ]