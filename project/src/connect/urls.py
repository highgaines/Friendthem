from django.urls import path
from src.connect import views

urlpatterns = [
    path('users/', views.connected_users_view, name='users'),
    path('', views.connection_view, name='connect'),
]
