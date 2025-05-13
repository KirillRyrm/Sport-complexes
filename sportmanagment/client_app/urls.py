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


]