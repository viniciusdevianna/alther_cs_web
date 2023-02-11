from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    re_path(r'^login/(?P<next>\w+)/$', views.login, name='login'),    
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('characters/', views.pick_character, name='pick_character'),
]