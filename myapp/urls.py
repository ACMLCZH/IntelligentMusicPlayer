from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.login, name='login'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('sign_in_sign_up_reset_request', views.backend_login_process, name='sign_in_sign_up_reset_request'),
    path('play/', views.play_music, name='play_music'),
    path('reorganize-playlist/', views.reorganize_playlist, name='reorganize_playlist'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)