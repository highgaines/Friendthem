from django.urls import path
from src.pictures import views

urlpatterns = [
    path('facebook/', views.facebook_pictures_view, name='facebook_pictures'),
]
