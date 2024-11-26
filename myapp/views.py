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

from rest_framework import generics
from .models import Song, Favlist, UserFav
from .serializers import SongSerializer, SongDocumentSerializer, FavlistSerializer, UserFavSerializer
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from .documents import SongDocument
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    CompoundSearchFilterBackend,
    OrderingFilterBackend,
)
from django_elasticsearch_dsl_drf.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated


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
        FilteringFilterBackend,
        OrderingFilterBackend,
        CompoundSearchFilterBackend,
    ]

    search_fields = {
        'name': {'boost': 2},
        'author': None,
        'lyrics': None,
    }

    filter_fields = {
        'name': 'name.raw',
        'author': 'author.raw',
        'lyrics': 'lyrics.raw',
    }

    ordering_fields = {
        'name': 'name.raw',
        'author': 'author.raw',
        'duration': 'duration',
    }
    ordering = ('name',)

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset)


class FavlistListCreateView(generics.ListCreateAPIView):
    queryset = Favlist.objects.all()
    serializer_class = FavlistSerializer

class FavlistRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Favlist.objects.all()
    serializer_class = FavlistSerializer


class UserFavListCreateView(ListCreateAPIView):
    queryset = UserFav.objects.all()
    serializer_class = UserFavSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Automatically set the user to the currently authenticated user
        serializer.save(user=self.request.user)

# Retrieve/Update/Delete API View
class UserFavDetailView(RetrieveUpdateDestroyAPIView):
    queryset = UserFav.objects.all()
    serializer_class = UserFavSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Ensure users can only access their own favorites
        return UserFav.objects.filter(user=self.request.user)
