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