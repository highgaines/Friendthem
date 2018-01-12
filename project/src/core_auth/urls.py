from django.urls import path
from src.core_auth import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('me/', views.user_details, name='me')
]
