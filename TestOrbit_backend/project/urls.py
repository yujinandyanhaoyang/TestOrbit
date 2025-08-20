from django.urls import path

from project import views

app_name = "project"

urlpatterns = [
    # 旧接口保留，兼容已有前端
    path('envir-view', views.ProjectView.as_view()),
    path('param-type', views.get_param_type),
    path('change-envir-position', views.change_project_position),

    # 新接口
    path('project-view', views.ProjectView.as_view()),
    path('change-project-position',  views.change_project_position),
    path('get-param-type', views.get_param_type),
]