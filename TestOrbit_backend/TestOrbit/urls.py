"""TestOrbit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from TestOrbit import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user.urls', namespace='user')),
    path('api-data/', include('apiData.urls', namespace='apiData')),

    path('put-file', views.put_file),

    # 旧接口，保留，兼容已有前端
    path('project/', include('config.urls', namespace='config_old')),
    path('conf/', include('project.urls', namespace='project_old')),
    # 新接口 解决历史名称错配技术债
    path('config/', include('config.urls', namespace='config')),
    path('project/', include('project.urls', namespace='project'))
]
