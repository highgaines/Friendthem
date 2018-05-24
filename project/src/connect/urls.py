from django.urls import path
from src.connect import views

urlpatterns = [
    path('users/', views.connected_users_view, name='users'),
    path('<int:user_id>/', views.connection_list_view, name='connection_list'),
    path('', views.connection_view, name='connect'),
]
