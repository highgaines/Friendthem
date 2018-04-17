from django.urls import path
from src.invite import views

urlpatterns = [
    path('', views.invite_view, name='invite'),
]
