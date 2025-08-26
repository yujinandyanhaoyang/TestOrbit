from django.urls import path
from user import views

app_name = "user"

urlpatterns = [
    path('login', views.login),
    path('user-view', views.UserView.as_view()),
    path('user-cfg-params', views.get_user_cfg_params),
    path('clear-user-temp-params', views.clear_user_temp_params),
    path('set-user-cfg', views.set_user_cfg),
    path('change-password', views.change_password),
    path('assign-projects', views.assign_user_projects),

    # 扩展
    # 分配用户到项目组
    path('assign-projects', views.assign_user_projects),
]
