from django.urls import path
from src.pictures import views

urlpatterns = [
    path('facebook/', views.facebook_pictures_view, name='facebook_pictures'),
    path('<pk>/', views.pictures_delete_update_view, name='pictures_delete_update'),
    path('', views.pictures_list_create_view, name='pictures'),
]
