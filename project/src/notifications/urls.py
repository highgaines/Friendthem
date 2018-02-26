from django.urls import path
from src.notifications import views

urlpatterns = [
    path('', views.notifications_view, name='notifications'),
    path('device/', views.add_device_view, name='add_device'),
    path('<pk>/', views.delete_notification_view, name='delete_notification')
]
