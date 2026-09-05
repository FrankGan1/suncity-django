from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('post-login/', views.post_login_redirect, name='post_login_redirect'),
    path('my-account/', views.my_account_view, name='my_account'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password_confirm_view, name='reset_password_confirm'),
]
