from django.urls import path
from . import views

urlpatterns = [
   #path('login/', views.auth_login, name='auth_login'),
   path('gym_list/', views.gym_list, name='gym_list'),
   path('gym_list/add/', views.add_gym, name='add_gym'),
    path('gym_list/edit/<int:gym_id>/', views.edit_gym, name='edit_gym'),
    path('gym_list/delete/<int:gym_id>/', views.delete_gym, name='delete_gym'),
    path('api/gyms/', views.GymListAPI.as_view(), name='gym_list_api'),

    path('equipment/', views.equipment_list, name='equipment_list'),
    path('equipment/add/', views.add_equipment, name='add_equipment'),
    path('equipment/edit/<int:equipment_id>/', views.edit_equipment, name='edit_equipment'),
    path('equipment/delete/<int:equipment_id>/', views.delete_equipment, name='delete_equipment'),
]