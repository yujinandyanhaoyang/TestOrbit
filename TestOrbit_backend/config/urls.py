from django.urls import path
from config import views

app_name = "config"

urlpatterns = [
    # 旧接口，兼容现有前端
    path('project-view', views.EnvironmentView.as_view()),
    path('project-overview', views.environment_overview),
    path('project-envir-data', views.get_project_envir_data),
    path('project-have-envir', views.get_project_have_envir),
    path('test-db-connect', views.test_db_connect),
    path('proj-db-database', views.get_proj_db_database),
    path('run-sql', views.run_sql),
    path('get-index-statistics', views.get_index_statistics),

    #新接口
    path('environment-view', views.EnvironmentView.as_view()),
    path('environment-overview', views.environment_overview),

]
