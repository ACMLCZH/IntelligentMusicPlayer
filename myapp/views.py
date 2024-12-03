from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login as auth_login
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse,HttpResponseRedirect
from django.contrib.auth.models import User
from django.urls import reverse

import json


from django.http import Http404
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Song, Favlist, UserFav
from .serializers import SongSerializer, SongDocumentSerializer, FavlistSerializer, UserFavSerializer, FavlistBasicSerializer
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from .documents import SongDocument
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    CompoundSearchFilterBackend,
    OrderingFilterBackend,
)
from django_elasticsearch_dsl_drf.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

import requests
from asgiref.sync import sync_to_async
from django.utils.decorators import method_decorator
from typing import List, Dict
import re
from openai import OpenAI
import os

@csrf_exempt
def login(request):
    return render(request, 'login.html')

@csrf_exempt
def sign_up(request):
    return render(request, 'sign_up.html')

@csrf_exempt
def reset_password(request):
    return render(request, 'reset_password.html')

@csrf_exempt
def backend_login_process(request):
    if request.method == 'POST':
        try: 
            data = json.loads(request.body) 
            request_type = data.get('type') 
            username = data.get('username') 
            password = data.get('password')
            confirm_password = data.get('confirm_password')
            print(request_type)
            print(username)
            print(password)
            print(confirm_password)
            
            if request_type == "sign_in":
                user = authenticate(request, username=username, password=password)
                
                if user is not None:
                    auth_login(request, user)
                    response = {
                    'response': 'Log In Successful!',
                    'redirect': True,
                    'redirect_url': reverse("index")
                    }
                    return JsonResponse(response,status=200)
                else:
                    messages.error(request, '用户名或密码错误')
                    return JsonResponse({'response': 'Invalid Username or Password'}, status=200)

            if request_type == "sign_up":                
                if confirm_password != password:
                    return JsonResponse({'response': 'Passwords are not the same!'}, status=200)
                
                if User.objects.filter(username=username).exists(): #
                    return JsonResponse({'response': 'Username already exists!'}, status=200) # 如果用户名不存在，可以继续创建用户的逻辑 
                
                user = User.objects.create_user(username=username, password=password) 
                print("create success!")
                response = {
                    'response': 'Sign Up Successful!',
                    'redirect': True,
                    'redirect_url': reverse("login")
                }
                print(response)
                return JsonResponse(response, status=200)
            
            if request_type == "reset":
                confirm_password = data.get('confirm_password')

                if not User.objects.filter(username=username).exists(): #
                    return JsonResponse({'response': 'Username not exists!'}, status=200) # 如果用户名不存在，可以继续创建用户的逻辑 
                if confirm_password != password:
                    return JsonResponse({'response': 'Passwords are not the same!'}, status=200)
                user = User.objects.get(username=username)
                user.set_password(password) 
                user.save()
                response = {
                    'response': 'Reset Successful!',
                    'redirect': True,
                    'redirect_url': reverse("login")
                }
                return JsonResponse(response, status=200)
        
        except json.JSONDecodeError: 
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        redirect("sign_up")
    return JsonResponse({'error': 'Invalid request'}, status=400)

    # render(request,'login.html')
    # return JsonResponse({'error': 'Invalid Username or Password'}, status=200)
    

@login_required(login_url='login')
def home(request):
    return render(request, 'templates/home.html')

from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    # Set empty initial state
    context = {
        'playlist': [],
        'current_track': {
            'id': 0,
            'title': 'Select a track to play',
            'artist': 'No track playing',
            'cover': '/static/default-cover.jpg',
            'url': ''
        },
        'current_index': -1
    }
    return render(request, 'index.html', context)

def get_playlist_from_api():
    """Fetch playlist data from API"""
    try:
        response = requests.get('http://127.0.0.1:8000/favlist/1/')
        if response.status_code == 200:
            data = response.json()
            # Transform API data to player format
            playlist = []
            for song in data.get('songs_detail', []):
                playlist.append({
                    'id': song['id'],
                    'title': song['name'],
                    'artist': song['author'],
                    'cover': song['cover_url'],
                    'url': song['mp3_url']
                })
            return playlist
        else:
            return []
    except Exception as e:
        print(f"Error fetching playlist: {e}")
        return []
    
@csrf_exempt
async def play_music(request):
    # Get playlist from API
    playlist = await sync_to_async(get_playlist_from_api)()
    if not playlist:
        return JsonResponse({'error': 'Failed to load playlist'}, status=500)
    
    # Get current track index from session
    current_index = request.session.get('current_track', 0)
    current_track = playlist[current_index].copy()
    
    context = {
        'playlist': playlist,
        'current_track': current_track,
        'current_index': current_index
    }
    return render(request, 'index.html', context)

# token = os.environ["GITHUB_TOKEN"]
token = "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" # a temporary token for testing
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o-mini"
class PlaylistOrganizer:
    def __init__(self):
        self.client = OpenAI(
            base_url=endpoint,
            api_key=token,
        )
        self.playlists = []
        
    async def search_songs_by_name(self, name: str) -> List[Dict]:
        # Stub - will be replaced with actual API call
        return [song for song in self.playlists if song['title'].lower() == name.lower()]
    
    async def search_songs_by_genre(self, genre: str) -> List[Dict]:
        # Stub - will be replaced with actual API call 
        return [song for song in self.playlists if song.get('genre','').lower() == genre.lower()]

    def parse_instruction(self, instruction: str) -> Dict:
        """Use GPT to parse the natural language instruction"""
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": """
                You are a music playlist organizer. Parse the user's instruction into a structured format.
                Return a JSON object with:
                - type: "pattern" or "genre"
                - song_name: (if pattern type)
                - interval: (if pattern type, integer) 
                - genre: (if genre type)
                """},
                {"role": "user", "content": instruction}
            ]
        )
        # Convert string response to Dict
        content = response.choices[0].message.content
        return json.loads(content)

    async def reorganize_playlist(self, instruction: str) -> List[Dict]:
        """Main method to reorganize playlist based on instruction"""
        print(f"Received instruction: {instruction}")
        parsed = self.parse_instruction(instruction)
        print(f"Parsed instruction: {parsed}")
        
        if parsed['type'] == 'pattern':
            print(f"Pattern-based reorganization: {parsed['song_name']} every {parsed['interval']} songs")
            # Handle pattern-based organization (e.g. "OMG every 2 songs")
            song = await self.search_songs_by_name(parsed['song_name'])
            if not song:
                raise ValueError(f"Song {parsed['song_name']} not found")
                
            interval = int(parsed['interval'])
            new_playlist = []
            other_songs = [s for s in self.playlists if s['title'] != song[0]['title']]
            
            # Insert requested song at every interval position
            j = 0  # Counter for other songs
            for i in range(len(self.playlists) + len(self.playlists)//interval):  # Extended length
                if i % (interval + 1) == 0:  # +1 because we want song after every N songs
                    new_playlist.append(song[0])
                else:
                    if j < len(other_songs):
                        new_playlist.append(other_songs[j])
                        j += 1
                        
        print(f"New playlist: {[s['title'] for s in new_playlist]}")
        return new_playlist

def _create_json_response(data, status=200):
    """Synchronous helper to create JsonResponse"""
    return JsonResponse(data, status=status)

def _update_session_and_respond(request, playlist):
    """Synchronous helper to update session and return response"""
    print("=== New Playlist ===")
    for song in playlist:
        print(f"Title: {song['title']}, Artist: {song['artist']}")
    print("=================")
    
    request.session['playlist'] = playlist
    request.session['current_track'] = 0  # Reset to first track
    return JsonResponse({
        'status': 'success',
        'playlist': playlist,
        'current_track': playlist[0] if playlist else None
    })

@csrf_exempt
async def reorganize_playlist(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            instruction = data.get('instruction')
            
            # Get playlist from API
            playlist = await sync_to_async(get_playlist_from_api)()
            
            organizer = PlaylistOrganizer()
            organizer.playlists = playlist
            
            new_playlist = await organizer.reorganize_playlist(instruction)
            
            # Wrap the entire session update and response in sync_to_async            
            return await sync_to_async(_update_session_and_respond)(request, new_playlist)
            
        except json.JSONDecodeError:
            return await sync_to_async(_create_json_response)(
                {'status': 'error', 'message': 'Invalid JSON data'}, 
                400
            )
            
        except Exception as e:
            return await sync_to_async(_create_json_response)(
                {'status': 'error', 'message': str(e)}, 
                500
            )
    
    return await sync_to_async(_create_json_response)(
        {'status': 'error', 'message': 'Method not allowed'},
        405
    )

class SongListCreateAPIView(generics.ListCreateAPIView):
    queryset = Song.objects.all()
    serializer_class = SongSerializer


class SongRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Song.objects.all()
    serializer_class = SongSerializer


class SongSearchView(DocumentViewSet):
    document = SongDocument
    serializer_class = SongDocumentSerializer
    pagination_class = LimitOffsetPagination

    filter_backends = [
        # FilteringFilterBackend,
        # OrderingFilterBackend,
        CompoundSearchFilterBackend,
    ]

    search_fields = {
        'name': {'boost': 5},
        'author': {'boost': 4},
        'album': {'boost': 3},
        'topics': {'boost': 2},
        'lyrics': {'boost': 1},
    }
    ordering = ('_score',)

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset)


class FavlistListCreateView(generics.ListCreateAPIView):
    queryset = Favlist.objects.all()
    serializer_class = FavlistSerializer


class FavlistRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Favlist.objects.all()
    serializer_class = FavlistSerializer

    def retrieve(self, request, *args, **kwargs):
        favlist = self.get_object()
        serializer = self.get_serializer(favlist)

        songs = favlist.songs.all()
        song_serializer = SongSerializer(songs, many=True)

        response_data = serializer.data
        response_data['songs_detail'] = song_serializer.data

        return Response(response_data)


class UserFavView(generics.GenericAPIView):
    serializer_class = UserFavSerializer
    queryset = UserFav.objects.all()

    def get_object(self):
        user = self.request.user
        user_fav, created = UserFav.objects.get_or_create(user=user)
        return user_fav
        # try:
        #     return UserFav.objects.get(user=self.request.user)
        # except UserFav.DoesNotExist:
        #     raise Http404("UserFav object does not exist for this user.")

    def get(self, request, *args, **kwargs):
        # Retrieve the UserFav object for the current user
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        favlists = instance.favlists.all()
        favlist_serializer = FavlistBasicSerializer(favlists, many=True)

        response_data = serializer.data
        response_data['favlists_detail'] = favlist_serializer.data

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
