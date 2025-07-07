from django.urls import path
from . import views

app_name = 'evaluation'

urlpatterns = [
    path('', views.project_list, name='project_list'),                     
    path('project/<int:pk>/', views.project_detail, name='project_detail'), 
    path('project/<int:pk>/vote/', views.project_vote, name='project_vote'), 
    path('project/<int:pk>/result/', views.project_result, name='project_result'), 
]
