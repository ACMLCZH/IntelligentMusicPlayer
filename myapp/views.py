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
    return render(request, 'index.html')


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

        if not instance.favlists.exists():
            # Create a new Favlist with default name
            default_favlist = Favlist.objects.create(name="My favorites")
            # Add the new Favlist to user's favlists
            instance.favlists.add(default_favlist)

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
