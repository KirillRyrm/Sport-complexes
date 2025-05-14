from django.urls import path
from . import views

urlpatterns = [
    path('client_profile/', views.client_profile, name='client_profile'),
    path('clients/', views.clients_list, name='clients_list'),
    path('create_profile/', views.create_profile, name='create_profile'),
    path('clients/delete/<int:user_id>/', views.delete_client, name='delete_client'),


    path('client_subscriptions/', views.client_subscriptions_list, name='client_subscriptions_list'),
    path('client_subscriptions/purchase/', views.purchase_subscription, name='purchase_subscription'),
    path('client_subscriptions/delete/<int:user_subscription_id>/', views.delete_subscription, name='delete_subscription'),


    path('client_goals/', views.client_goals_list, name='client_goals_list'),
    path('client_goals/add/', views.add_client_goal, name='add_client_goal'),
    path('client_goals/edit/<int:client_goal_id>/', views.edit_client_goal, name='edit_client_goal'),
    path('client_goals/delete/<int:client_goal_id>/', views.delete_client_goal, name='delete_client_goal'),

    path('client_feedbacks/', views.client_feedbacks_list, name='client_feedbacks_list'),
    path('client_feedbacks/add/', views.add_client_feedback, name='add_client_feedback'),
    path('client_feedbacks/edit/<int:feedback_id>/', views.edit_client_feedback, name='edit_client_feedback'),
    path('client_feedbacks/delete/<int:feedback_id>/', views.delete_client_feedback, name='delete_client_feedback'),

    path('assign_trainer/<int:trainer_id>/', views.assign_trainer, name='assign_trainer'),

]