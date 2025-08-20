"""
简单的URL路由检查
只打印主要URL路由
"""
from django.conf import settings
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TestOrbit.settings')
django.setup()

# 获取主要的URLs
from TestOrbit.urls import urlpatterns

print("\n=== 主项目URL配置 ===")
for pattern in urlpatterns:
    print(f"- {pattern}")

# 检查关键的应用URLs
print("\n=== project应用URL ===")
from project.urls import urlpatterns as project_urls
for pattern in project_urls:
    print(f"- {pattern}")

print("\n=== config应用URL ===")
from config.urls import urlpatterns as config_urls
for pattern in config_urls:
    print(f"- {pattern}")

print("\n检查完成！")
