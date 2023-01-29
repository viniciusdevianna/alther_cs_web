from django.urls import path
from . import views

urlpatterns = [
    path('main/', views.main, name='main'),
    path('roll_action/<int:action_ID>', views.roll_action, name='roll_action'),
]