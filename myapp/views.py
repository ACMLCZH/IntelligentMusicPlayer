# myapp/views.py

import json
import requests
from asgiref.sync import sync_to_async
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseRedirect
from django.http import Http404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    CompoundSearchFilterBackend,
    OrderingFilterBackend,
)
from django_elasticsearch_dsl_drf.pagination import LimitOffsetPagination

from .models import Song, Favlist, UserFav
from .serializers import (
    SongSerializer,
    SongDocumentSerializer,
    FavlistSerializer,
    UserFavSerializer,
    FavlistBasicSerializer,
)
from .documents import SongDocument
from music_ai.tools import generate_songs, PlaylistOrganizer


@csrf_exempt
def login(request):
    return render(request, "login.html")


@csrf_exempt
def sign_up(request):
    return render(request, "sign_up.html")


@csrf_exempt
def reset_password(request):
    return render(request, "reset_password.html")


@csrf_exempt
def backend_login_process(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            request_type = data.get("type")
            username = data.get("username")
            password = data.get("password")
            confirm_password = data.get("confirm_password")
            security_code = data.get("security_code")

            if request_type == "sign_in":
                user = authenticate(request, username=username, password=password)

                if user is not None:
                    auth_login(request, user)
                    response = {
                        "response": "Log In Successful!",
                        "redirect": True,
                        "redirect_url": reverse("index"),
                    }
                    return JsonResponse(response, status=200)
                else:
                    messages.error(request, "Invalid Username or Password")
                    return JsonResponse(
                        {"response": "Invalid Username or Password"}, status=200
                    )

            if request_type == "sign_up":
                if confirm_password != password:
                    return JsonResponse(
                        {"response": "Passwords are not the same!"}, status=200
                    )

                if User.objects.filter(username=username).exists():
                    return JsonResponse(
                        {"response": "Username already exists!"}, status=200
                    )

                user = User.objects.create_user(username=username, password=password)
                response = {
                    "response": "Sign Up Successful!",
                    "redirect": True,
                    "redirect_url": reverse("login"),
                }
                return JsonResponse(response, status=200)

            if request_type == "reset":
                confirm_password = data.get("confirm_password")

                if not User.objects.filter(username=username).exists():  #
                    return JsonResponse(
                        {"response": "Username not exists!"}, status=200
                    )
                if security_code != "0000":
                    return JsonResponse(
                        {
                            "response": "Wrong security code!!! Please ask administrator!!!"
                        },
                        status=200,
                    )
                if confirm_password != password:
                    return JsonResponse(
                        {"response": "Passwords are not the same!"}, status=200
                    )
                user = User.objects.get(username=username)
                user.set_password(password)
                user.save()
                response = {
                    "response": "Reset Successful!",
                    "redirect": True,
                    "redirect_url": reverse("login"),
                }
                return JsonResponse(response, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        redirect("sign_up")
    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def index(request):
    # Set empty initial state
    context = {
        "playlist": [],
        "current_track": {
            "id": 0,
            "title": "Select a track to play",
            "artist": "No track playing",
            "cover": "/static/default-cover.jpg",
            "url": "",
        },
        "current_index": -1,
    }
    return render(request, "index.html", context)


def get_playlist_from_api(playlist_id):
    """Fetch playlist data from API"""

    favlist = Favlist.objects.get(id=playlist_id)
    songs = favlist.songs.all()
    song_serializer = SongSerializer(songs, many=True)
    playlist = []
    for song in song_serializer.data:
        playlist.append(
            {
                "id": song["id"],
                "title": song["name"],
                "artist": song["author"],
                "cover": song["cover_url"],
                "url": song["mp3_url"],
            }
        )
    return playlist


@csrf_exempt
async def play_music(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            playlist_id = data.get('playlist_id')
            track_index = data.get('track_index', 0)

            if not playlist_id:
                return JsonResponse({"status": "error", "message": "Missing playlist_id"}, status=400)

            # Get playlist using the provided ID
            playlist = await sync_to_async(get_playlist_from_api)(playlist_id)
            
            if not playlist:
                return JsonResponse({"status": "error", "message": "Playlist not found"}, status=404)

            return JsonResponse({
                "status": "success",
                "playlist": playlist,
                "current_index": track_index
            })

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)


def _create_json_response(data, status=200):
    """Synchronous helper to create JsonResponse"""
    return JsonResponse(data, status=status)


@csrf_exempt
async def reorganize_playlist(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            instruction = data.get("instruction")
            queue = data.get("queue")  # Get queue instead of playlist_id

            # Create organizer with current queue
            organizer = PlaylistOrganizer(queue)
            new_queue = await organizer.reorganize_playlist(instruction)

            return await sync_to_async(_create_json_response)(
                {"status": "success", "playlist": new_queue}
            )

        except json.JSONDecodeError:
            return await sync_to_async(_create_json_response)(
                {"status": "error", "message": "Invalid JSON data"}, 400
            )
        except Exception as e:
            return await sync_to_async(_create_json_response)(
                {"status": "error", "message": str(e)}, 500
            )
    return await sync_to_async(_create_json_response)(
        {"status": "error", "message": "Method not allowed"}, 405
    )


class IsSuperUserOrReadOnly(IsAuthenticated):
    def has_permission(self, request, view):
        # Allow read-only methods for any authenticated user
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        # Only superuser can create, update, or destroy
        if request.user and request.user.is_superuser:
            return True
        return False


class SongListCreateAPIView(generics.ListCreateAPIView):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    permission_classes = [IsSuperUserOrReadOnly]


class SongRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    permission_classes = [IsSuperUserOrReadOnly]


class SongSearchView(DocumentViewSet):
    document = SongDocument
    serializer_class = SongDocumentSerializer
    pagination_class = LimitOffsetPagination

    filter_backends = [
        CompoundSearchFilterBackend,
    ]

    search_fields = {
        "name": {"boost": 5},
        "author": {"boost": 4},
        "album": {"boost": 3},
        "topics": {"boost": 2},
        "lyrics": {"boost": 1},
    }
    ordering = ("_score",)

    def filter_queryset(self, queryset):
        field = self.request.query_params.get("field", None)
        search = self.request.query_params.get("search", None)
        ai = self.request.query_params.get("ai", None)

        # Exclude results where author is "SunoAI"
        if ai != "True":
            queryset = queryset.query(
                "bool", must_not=[{"match": {"author": "SunoAI"}}]
            )

        if field and search:
            if field in self.search_fields:
                return queryset.query("match", **{field: search})
            else:
                raise ValidationError(f"Field '{field}' is not a valid search field.")
        return super().filter_queryset(queryset)


class FavlistListCreateView(generics.ListCreateAPIView):
    queryset = Favlist.objects.all()
    serializer_class = FavlistSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class FavlistRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Favlist.objects.all()
    serializer_class = FavlistSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        if self.get_object().owner != self.request.user:
            raise PermissionDenied("You do not have permission to edit this Favlist.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise PermissionDenied("You do not have permission to delete this Favlist.")
        instance.delete()

    def retrieve(self, request, *args, **kwargs):
        favlist = self.get_object()
        serializer = self.get_serializer(favlist)

        songs = favlist.songs.all()
        song_serializer = SongSerializer(songs, many=True)

        response_data = serializer.data
        response_data["songs_detail"] = song_serializer.data

        return Response(response_data)


class UserFavView(generics.GenericAPIView):
    queryset = UserFav.objects.all()
    serializer_class = UserFavSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        user_fav, created = UserFav.objects.get_or_create(user=user)
        return user_fav

    def get(self, request, *args, **kwargs):
        # Retrieve the UserFav object for the current user
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        if not instance.favlists.exists():
            # Create a new Favlist with default name
            default_favlist = Favlist.objects.create(
                name="My favorites", owner=request.user
            )
            # Add the new Favlist to user's favlists
            instance.favlists.add(default_favlist)

        favlists = instance.favlists.all()
        favlist_serializer = FavlistBasicSerializer(favlists, many=True)

        response_data = serializer.data
        response_data["favlists_detail"] = favlist_serializer.data

        return Response(response_data)

    def post(self, request, *args, **kwargs):
        # Check if UserFav already exists for this user
        if UserFav.objects.filter(user=request.user).exists():
            raise ValidationError("UserFav already exists for this user.")
        # Create a new UserFav object
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        # Update the UserFav object
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        # Partially update the UserFav object
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        # Delete the UserFav object
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenerateSongsView(generics.GenericAPIView):
    queryset = Favlist.objects.all()
    serializer_class = UserFavSerializer

    def get(self, request, *args, **kwargs):
        favlist = self.get_object()
        favlist_songs = favlist.songs.all()
        favlist_songs_serial = SongSerializer(favlist_songs, many=True)

        generate_results = generate_songs(favlist_songs_serial.data)
        generate_list = list()
        for generate_result in generate_results:
            generate_song = Song.objects.create(**generate_result)
            generate_list.append(SongSerializer(generate_song).data)

        return Response(generate_list)


@csrf_exempt
def custom_logout(request):
    if request.method == "POST":
        logout(request)
        return JsonResponse({"message": "Logged out successfully."})
    else:
        return JsonResponse({"error": "Invalid request method."}, status=400)
