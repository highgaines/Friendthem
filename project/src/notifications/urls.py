from django.urls import path
from src.notifications import views

urlpatterns = [
    path('device/', views.add_device_view, name='add_device'),
]
