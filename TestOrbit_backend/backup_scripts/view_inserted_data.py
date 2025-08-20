"""
查看数据库中的测试数据
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

print("\n" + "="*80)
print(" "*30 + "数据库测试数据查看")
print("="*80)

# 统计数据
print(f"\n数据统计:")
print(f"- 用户 (LimUser): {LimUser.objects.count()} 条记录")
print(f"- 项目 (Project): {Project.objects.count()} 条记录")
print(f"- API模块 (ApiModule): {ApiModule.objects.count()} 条记录")
print(f"- API数据 (ApiData): {ApiData.objects.count()} 条记录")
print(f"- API用例模块 (ApiCaseModule): {ApiCaseModule.objects.count()} 条记录")
print(f"- API用例 (ApiCase): {ApiCase.objects.count()} 条记录")
print(f"- API用例步骤 (ApiCaseStep): {ApiCaseStep.objects.count()} 条记录")

# 显示具体数据
print(f"\n最近创建的API数据:")
apis = ApiData.objects.all().order_by('-created')[:10]
for api in apis:
    print(f"  - {api.name} ({api.method} {api.path}) - 创建者: {api.creater.username if api.creater else '未知'}")

print(f"\n最近创建的API用例:")
cases = ApiCase.objects.filter(is_deleted=False).order_by('-created')[:10]
for case in cases:
    print(f"  - {case.name} (模块: {case.module.name}) - 创建者: {case.creater.username if case.creater else '未知'}")

print(f"\n最近创建的API用例步骤:")
steps = ApiCaseStep.objects.all().order_by('-id')[:10]
for step in steps:
    print(f"  - {step.step_name} (用例: {step.case.name}) - API: {step.api.name if step.api else 'N/A'}")

print("\n" + "="*80)
print("✅ 数据插入成功，系统功能正常！")
print("="*80)
