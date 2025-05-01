from django.urls import path
from . import views
#from api import views

urlpatterns = [
    path('', views.home, name='home'),            # Головна сторінка
    path('register/', views.register, name='register'),  # Реєстрація
    path('login/', views.login_view, name='login'),      # Логін
    path('logout/', views.logout_view, name='logout'),   # Логаут

    # API-ендпоінти
    path('api/register/', views.api_register, name='api_register'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/user-info/', views.api_user_info, name='api_user_info'),
    path('api/check-user/', views.api_check_user, name='api_check_user'),
]