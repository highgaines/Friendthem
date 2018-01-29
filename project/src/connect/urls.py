from django.urls import path
from src.connect import views

urlpatterns = [
    path('/', views.connection_view, name='connect'),
]
