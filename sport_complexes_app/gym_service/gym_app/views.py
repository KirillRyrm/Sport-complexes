import requests
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, permission_required
from .models import Gym
from django.contrib.auth.models import User
import logging


def auth_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            response = requests.post(
                'http://127.0.0.1:8000/api/login/',
                data={'username': username, 'password': password},
                timeout=5
            )
            if response.status_code == 200:
                user_data = response.json()
                # Створюємо тимчасовий об'єкт User
                user = User(username=user_data['username'])
                user.is_authenticated = True
                user.is_active = True
                # Зберігаємо дозволи в сесії
                request.session['permissions'] = user_data.get('permissions', [])
                request.session['user_role'] = user_data['role']
                login(request, user)
                return redirect('gym_list')
            else:
                return render(request, 'gym_app/login_redirect.html', {'error': 'Невірні дані'})
        except requests.RequestException as e:
            return render(request, 'gym_app/login_redirect.html', {'error': 'Помилка сервісу авторизації'})
    return render(request, 'gym_app/login_redirect.html')

# @login_required
# @permission_required('auth_app.view_gyms', raise_exception=True)

def gym_list(request):
    gyms = Gym.objects.all()
    return render(request, 'gym_app/gym_list.html', {'gyms': gyms})

def check_permission(user, perm, obj=None):
    permissions = user.session.get('permissions', [])
    return perm in permissions

# Патчимо User для підтримки has_perm
User.has_perm = check_permission



def home(request):
    return render(request, 'gym_app/home.html', {
        'user_role': request.user.user_role,
        'username': request.user.username
    })