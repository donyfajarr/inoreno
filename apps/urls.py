from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),
    path('confirmation/<str:id>', views.confirmation, name='confirmation'),
    path('listproject', views.listproject, name='listproject'),
    path('newproject', views.newproject, name='newproject'),
    path('updateproject/<str:id>', views.updateproject, name='updateproject'),
    path('deleteproject/<str:id>', views.deleteproject, name='deleteproject'),
    path('listissue/<str:id>', views.listissue, name='listissue'),
    path('listdetails/<str:id>', views.listdetails, name='listdetails'),
    path('newissue', views.newissue, name='newissue'),
    path('updateissue/<str:id>', views.updateissue, name='updateissue'),
    path('deleteissue/<str:id>', views.deleteissue, name='deleteissue'),
    path('deleteproject/<str:id>', views.deleteproject, name='deleteproject'),
    path('settings', views.settings, name='settings'),
    path('get_project_data', views.get_project_data, name='get_project_data'),
    path('addissue', views.addissue, name='addissue'),
    path('send_email', views.send_email, name='send_email'),
    path('register', views.register, name='register'),
    path('export/csv/<int:id>/', views.export_csv, name='export_csv'),
]