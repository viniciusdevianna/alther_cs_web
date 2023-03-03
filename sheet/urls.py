from django.urls import path, re_path
from . import views

urlpatterns = [
    path('main/', views.main, name='main'),
    path('main/<int:char_ID>/', views.main, name='main'),
    path('roll_action/', views.roll_action, name='roll_action'),
    path('level_up/', views.level_up, name='level_up'),
    path('update/basic/', views.update_basic, name="update_basic"),
    path('update/bg/<int:char_ID>', views.update_bg, name='update_bg'),
    path('update/active/path/', views.change_active_path, name='change_active_path'),
    path('update/actions/<int:char_ID>', views.update_actions, name='update_actions'),
    path('create/', views.create_character, name='create'),
    path('path/new/<int:char_ID>/', views.new_path, name='new_path'),
    path('manipulate/attribute/', views.manipulate_attribute, name='manipulate_attr'),
    path('manipulate/pathpoints/', views.manipulate_pathpoints, name='manipulate_pathtpoints'),
    path('update/attributes/<int:char_ID>/', views.update_attributes, name='update_attributes'),
    path('update/text/', views.update_text, name='update_text'),
    path('evolve/<int:char_ID>/', views.evolve, name='evolve'),
    path('upgrade/attribute/', views.upgrade_attribute, name='upgrade_attribute'),
    path('upgrade/action/', views.upgrade_action, name='upgrade_action'),
    path('upgrade/character/battle/', views.upgrade_character_battle_actions, name='upgrade_char_battle'),
    path('skills/<int:char_ID>/', views.skills, name='skills'),
    path('skills/equip/', views.equip_skill, name='equip_skill'),
]