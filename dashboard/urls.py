from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('clients/add/', views.add_client, name='add_client'),
    path('clients/<int:client_id>/delete/', views.delete_client, name='delete_client'),
    path('clients/<int:client_id>/send-reset/', views.send_reset_password, name='send_reset_password'),
]
