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
                    'redirect_url': reverse("sign_up") #TODO:change to home url
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

# For test purpose. In production, this should be stored in a database, and get the playlist from there
PLAYLIST = [
        {
            'id': 0,
            'title': 'How Sweet',
            'artist': 'NewJeans',
            # 'url': 'https://soundcloud.com/newjeans-music/how-sweet?si=6b0954ced9ff456f8d833308603c9608&utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing'
            'cover': 'https://archive.org/download/How-Sweet-by-newjeans/How%20Sweet%20cover%20art.jpg',
            'url': 'https://archive.org/download/How-Sweet-by-newjeans/01.%20How%20Sweet.mp3'
        },
        {
            'id': 1, 
            'title': 'Supernatural',
            'artist': 'NewJeans',
            # 'url': 'https://soundcloud.com/newjeans-music/supernatural?si=2771a5c6ee9d4c868012132f8f3cf0a3&utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing'
            'cover': 'https://archive.org/download/02.-right-now/cover.jpg',
            'url': 'https://archive.org/download/02.-right-now/01.%20Supernatural.mp3'
            # 'topic': 'pop'
        },
        {
            'id': 2,
            'title': 'OMG',
            'artist': 'NewJeans', 
            # 'url': 'https://soundcloud.com/newjeans-music/omg?si=de039408a8c94b068087a9a5a7784914&utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing'
            'cover': 'https://archive.org/download/newjeans-omg-1st-single-album/cover.jpg',
            'url': 'https://archive.org/download/newjeans-omg-1st-single-album/01.%20OMG.mp3'
        }
    ]

def play_music(request):
    current_index = request.session.get('current_track', 0)
    current_track = PLAYLIST[current_index].copy()
    
    context = {
        'playlist': PLAYLIST,
        'current_track': current_track,
        'current_index': current_index
    }
    return render(request, 'play_music.html', context)

# LLM feature
from typing import List, Dict
import re
from openai import OpenAI
import os

# import json
from asgiref.sync import sync_to_async
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

token = os.environ["GITHUB_TOKEN"]
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

# @login_required(login_url='login')
@csrf_exempt
async def reorganize_playlist(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            instruction = data.get('instruction')
            
            organizer = PlaylistOrganizer()
            organizer.playlists = PLAYLIST
            
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