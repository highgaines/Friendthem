from django.urls import path

from src.competition import views

urlpatterns = [
    path('', views.retrieve_competition_user, name='competition_auth_user'),
    path('<int:user_id>/', views.retrieve_competition_user, name='competition_user'),
]
