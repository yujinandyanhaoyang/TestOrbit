from django.urls import path

from project import views

app_name = "project"

urlpatterns = [
    # 注释掉不存在的视图引用
    path('envir-view', views.ProjectView.as_view()),
    path('param-type', views.get_param_type),
    # 注释掉不存在的视图函数
    # path('change-envir-position', views.change_envir_position),
]
