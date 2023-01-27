from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('roll_action/<int:action_ID>', views.roll_action, name='roll_action'),
]