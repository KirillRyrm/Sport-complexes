from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.models import Group
from .models import UserCredentials

def register(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in')
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        # Валідація
        if not username or not password or not password_confirm:
            messages.error(request, 'All fields are required')
        elif len(username) < 3:
            messages.error(request, 'Username must be at least 3 characters long')
        elif len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long')
        elif password != password_confirm:
            messages.error(request, 'Passwords do not match')
        elif UserCredentials.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
        else:
            # Створення користувача
            user = UserCredentials(
                username=username,
                password=make_password(password),
                user_role='client'
            )
            user.save()

            # Додавання до групи client
            try:
                client_group = Group.objects.get(name='client')
                user.groups.add(client_group)
                messages.success(request, 'Registration successful! Please log in.')
                return redirect('login')
            except Group.DoesNotExist:
                messages.error(request, 'Error: Client group not found. Contact admin.')
                user.delete()
    return render(request, 'auth_app/register.html')

def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in')
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Валідація
        if not username or not password:
            messages.error(request, 'Username and password are required')
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password')
    return render(request, 'auth_app/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect('login')

@login_required
def home(request):
    return render(request, 'auth_app/home.html', {
        'user_role': request.user.user_role,
        'username': request.user.username
    })