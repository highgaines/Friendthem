from django.urls import path
from src.feed import views

urlpatterns = [
    path('<int:user_id>/<str:provider>/', views.feed_view, name='feed'),
]
