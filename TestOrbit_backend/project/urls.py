from django.urls import path

from project import views

app_name = "project"

urlpatterns = [
    path('project-view', views.ProjectView.as_view()),
    path('change-project-position',  views.change_project_position),
    path('get-param-type', views.get_param_type),
]