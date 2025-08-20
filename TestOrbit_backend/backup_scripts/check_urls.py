"""
URL路由检查脚本
检查项目中的URL路由是否正确配置
"""
from django.core.management import call_command
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TestOrbit.settings')
django.setup()

# 导入URL模块
from django.urls import get_resolver, get_urlconf
from django.urls.resolvers import URLPattern, URLResolver

def print_urlpatterns(urlpatterns, indent=0):
    """递归打印URL模式"""
    for pattern in urlpatterns:
        if isinstance(pattern, URLPattern):
            pattern_str = str(pattern.pattern)
            view_name = pattern.callback.__name__ if pattern.callback else str(pattern.callback)
            print(f"{' ' * indent}- {pattern_str} -> {view_name}")
        elif isinstance(pattern, URLResolver):
            print(f"{' ' * indent}+ [{pattern.pattern}] Namespace: {pattern.namespace}")
            print_urlpatterns(pattern.url_patterns, indent + 4)

print("\n=== TestOrbit URL路由配置 ===")
resolver = get_resolver()
print_urlpatterns(resolver.url_patterns)

print("\n=== 检查关键路径 ===")
paths = [
    '/project/project-view',
    '/project/change-project-position', 
    '/project/get-param-type',
    '/config/environment-view',
    '/config/environment-overview',
    '/config/test-db-connect',
    '/conf/envir-view',
]

for path in paths:
    try:
        match = resolver.resolve(path.lstrip('/'))
        print(f"✅ 路径 {path} 映射到: {match.func.__name__ if hasattr(match.func, '__name__') else match.func.__class__.__name__}")
    except Exception as e:
        print(f"❌ 路径 {path} 不存在: {str(e)}")

print("\n检查完成！")
