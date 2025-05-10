from django.urls import path
from . import views

urlpatterns = [
    path('training_types/', views.training_type_list, name='training_type_list'),
    path('training_types/add/', views.add_training_type, name='add_training_type'),
    path('training_types/edit/<int:training_type_id>/', views.edit_training_type, name='edit_training_type'),
    path('training_types/delete/<int:training_type_id>/', views.delete_training_type, name='delete_training_type'),


    path('profile/', views.trainer_profile, name='trainer_profile'),
]