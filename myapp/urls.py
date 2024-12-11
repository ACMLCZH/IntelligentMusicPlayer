# myapp/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("login/", views.login, name="login"),
    path("sign_up/", views.sign_up, name="sign_up"),
    path("reset_password/", views.reset_password, name="reset_password"),
    path(
        "sign_in_sign_up_reset_request",
        views.backend_login_process,
        name="sign_in_sign_up_reset_request",
    ),
    path("song/", views.SongListCreateAPIView.as_view(), name="song-list-create"),
    path(
        "song/<int:pk>/",
        views.SongRetrieveUpdateDestroyAPIView.as_view(),
        name="song-detail",
    ),
    path(
        "song/search/",
        views.SongSearchView.as_view({"get": "list"}),
        name="song-search",
    ),
    path("favlist/", views.FavlistListCreateView.as_view(), name="favlist-list-create"),
    path(
        "favlist/<int:pk>/",
        views.FavlistRetrieveUpdateDestroyView.as_view(),
        name="favlist-detail",
    ),
    path("userfav/", views.UserFavView.as_view(), name="userfav"),
    path("index/", views.index, name="index"),
    path("reorganize-playlist/", views.reorganize_playlist, name="reorganize-playlist"),
    path(
        "generate-songs/<int:pk>/",
        views.GenerateSongsView.as_view(),
        name="generate-songs",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
