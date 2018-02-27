from django.urls import path
from src.pictures import views

urlpatterns = [
    path('', views.pictures_view, name='pictures'),
]
