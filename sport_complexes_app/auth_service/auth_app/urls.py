from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),            # Головна сторінка
    path('register/', views.register, name='register'),  # Реєстрація
    path('login/', views.login_view, name='login'),      # Логін
    path('logout/', views.logout_view, name='logout'),   # Логаут
]