"""
检查数据库中的数据状态
"""
import os
import sys

# 添加父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TestOrbit.settings')
import django
django.setup()

# 导入模型
from apiData.models import ApiModule, ApiData, ApiCaseModule, ApiCase, ApiCaseStep
from project.models import Project
from user.models import LimUser

print("\n" + "="*60)
print(" "*20 + "数据库状态检查")
print("="*60)

# 检查数据库中的记录数
print(f"\n当前数据统计:")
print(f"- 用户 (LimUser): {LimUser.objects.count()} 条记录")
print(f"- 项目 (Project): {Project.objects.count()} 条记录")
print(f"- API模块 (ApiModule): {ApiModule.objects.count()} 条记录")
print(f"- API数据 (ApiData): {ApiData.objects.count()} 条记录")
print(f"- API用例模块 (ApiCaseModule): {ApiCaseModule.objects.count()} 条记录")
print(f"- API用例 (ApiCase): {ApiCase.objects.count()} 条记录")
print(f"- API用例步骤 (ApiCaseStep): {ApiCaseStep.objects.count()} 条记录")

# 显示现有数据详情
print(f"\n详细信息:")

# 用户信息
users = LimUser.objects.all()[:5]
if users:
    print(f"\n现有用户:")
    for user in users:
        print(f"  - {user.username} ({user.email})")

# 项目信息
projects = Project.objects.all()[:5]
if projects:
    print(f"\n现有项目:")
    for project in projects:
        print(f"  - {project.name} (ID: {project.id})")

# API模块信息
modules = ApiModule.objects.all()[:5]
if modules:
    print(f"\n现有API模块:")
    for module in modules:
        print(f"  - {module.name} (ID: {module.id}, 项目: {module.project.name})")

print("\n" + "="*60)
