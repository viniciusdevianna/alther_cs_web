from django.urls import path
from . import views

urlpatterns = [
    path('main/<int:char_ID>/', views.main, name='main'),
    path('roll_action/<int:action_ID>/', views.roll_action, name='roll_action'),
    path('create/', views.create_character, name='create'),
    path('update/attributes/<int:char_ID>/', views.update_attributes, name='update_attributes'),
    path('skills/<int:char_ID>/', views.skills, name='skills'),
]