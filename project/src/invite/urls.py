from django.urls import path
from django.views.generic import TemplateView
from src.invite import views

urlpatterns = [
    path('check/<int:user_id>/',
         views.check_invite_view,
         name='check_invite'),
]
