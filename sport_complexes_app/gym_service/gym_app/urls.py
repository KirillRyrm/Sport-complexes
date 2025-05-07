from django.urls import path
from . import views

urlpatterns = [
   path('', views.home, name='home'),
   #path('login/', views.auth_login, name='auth_login'),
   path('gym_list/', views.gym_list, name='gym_list'),
]