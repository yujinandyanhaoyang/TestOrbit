"""
批量插入5条测试数据到apiData各个表中
"""
import os
import sys
import random
from datetime import datetime, timedelta

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
from utils.constant import WAITING, SUCCESS, FAILED, USER_API
from django.db import transaction

print("\n" + "="*80)
print(" "*30 + "批量插入测试数据")
print("="*80)

try:
    # 确保有基础数据
    print("1. 准备基础数据...")
    
    # 创建测试用户
    users = []
    for i in range(3):
        user, created = LimUser.objects.get_or_create(
            username=f"testuser{i+1}",
            defaults={
                'email': f'testuser{i+1}@example.com',
                'is_staff': True,
                'real_name': f'测试用户{i+1}'
            }
        )
        if created:
            user.set_password("password123")
            user.save()
        users.append(user)
    print(f"   准备了 {len(users)} 个测试用户")

    # 创建测试项目
    projects = []
    for i in range(2):
        project, created = Project.objects.get_or_create(
            name=f"测试项目{i+1}",
            defaults={'position': i+1}
        )
        projects.append(project)
    print(f"   准备了 {len(projects)} 个测试项目")

    with transaction.atomic():
        # 2. 创建5个API模块
        print("\n2. 创建API模块...")
        api_modules = []
        for i in range(5):
            module = ApiModule.objects.create(
                name=f"API模块-{i+1}",
                project=random.choice(projects),
                module_related=[]
            )
            api_modules.append(module)
            print(f"   ✅ 创建: {module.name} (ID: {module.id})")

        # 3. 创建5个API数据
        print("\n3. 创建API数据...")
        api_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        api_data_list = []
        for i in range(5):
            api = ApiData.objects.create(
                name=f"测试接口-{i+1}",
                path=f"/api/v1/test{i+1}",
                method=api_methods[i],
                status=random.choice([WAITING, SUCCESS, FAILED]),
                project=random.choice(projects),
                default_params={
                    "headers": {"Content-Type": "application/json"},
                    "params": {f"param{i+1}": f"value{i+1}"}
                },
                timeout=random.randint(10, 60),
                module=random.choice(api_modules),
                source=USER_API,
                creater=random.choice(users)
            )
            api_data_list.append(api)
            print(f"   ✅ 创建: {api.name} ({api.method} {api.path})")

        # 4. 创建5个API用例模块
        print("\n4. 创建API用例模块...")
        case_modules = []
        # 使用时间戳确保ID唯一
        timestamp_suffix = str(int(datetime.now().timestamp()))[-6:]
        for i in range(5):
            unique_id = f"ACM{timestamp_suffix}{str(i+1).zfill(2)}"
            module = ApiCaseModule.objects.create(
                id=unique_id,
                name=f"用例模块-{i+1}",
                position=i+1
            )
            case_modules.append(module)
            print(f"   ✅ 创建: {module.name} (ID: {module.id})")

        # 5. 创建5个API测试用例
        print("\n5. 创建API测试用例...")
        api_cases = []
        for i in range(5):
            case = ApiCase.objects.create(
                name=f"测试用例-{i+1}",
                module=random.choice(case_modules),
                status=random.choice([WAITING, SUCCESS, FAILED]),
                remark=f"这是第{i+1}个测试用例的说明",
                is_deleted=False,
                latest_run_time=datetime.now() - timedelta(days=random.randint(0, 10)),
                position=i+1,
                creater=random.choice(users)
            )
            api_cases.append(case)
            print(f"   ✅ 创建: {case.name} (模块: {case.module.name})")

        # 6. 创建5个API用例步骤
        print("\n6. 创建API用例步骤...")
        for i in range(5):
            step = ApiCaseStep.objects.create(
                step_name=f"测试步骤-{i+1}",
                type="api",
                status=random.choice([WAITING, SUCCESS, FAILED]),
                params={
                    "request_type": "json",
                    "data": {f"key{i+1}": f"value{i+1}"}
                },
                api=random.choice(api_data_list),
                enabled=True,
                controller_data=None,
                quote_case=None,
                retried_times=0,
                case=random.choice(api_cases),
                results=None
            )
            print(f"   ✅ 创建: {step.step_name} (用例: {step.case.name})")

    print("\n" + "="*80)
    print(" "*25 + "数据插入完成")
    print("="*80)

    # 验证最终数据
    print(f"\n最终数据统计:")
    print(f"- 用户 (LimUser): {LimUser.objects.count()} 条记录")
    print(f"- 项目 (Project): {Project.objects.count()} 条记录")
    print(f"- API模块 (ApiModule): {ApiModule.objects.count()} 条记录")
    print(f"- API数据 (ApiData): {ApiData.objects.count()} 条记录")
    print(f"- API用例模块 (ApiCaseModule): {ApiCaseModule.objects.count()} 条记录")
    print(f"- API用例 (ApiCase): {ApiCase.objects.count()} 条记录")
    print(f"- API用例步骤 (ApiCaseStep): {ApiCaseStep.objects.count()} 条记录")

    print("\n🎉 所有测试数据插入成功！")

except Exception as e:
    print(f"\n❌ 错误: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
