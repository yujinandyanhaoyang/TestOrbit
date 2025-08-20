"""
简单的数据插入测试
直接插入一些测试数据并验证
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
from utils.constant import WAITING, SUCCESS, USER_API
from django.db import transaction

print("开始数据插入测试...")

try:
    # 1. 创建或获取测试用户
    print("1. 检查/创建测试用户...")
    user, created = LimUser.objects.get_or_create(
        username="testuser123",
        defaults={
            'email': 'testuser123@example.com',
            'is_staff': True,
            'real_name': '测试用户'
        }
    )
    if created:
        user.set_password("testpassword")
        user.save()
        print(f"   ✅ 创建新用户: {user.username}")
    else:
        print(f"   ✅ 使用现有用户: {user.username}")

    # 2. 创建或获取测试项目
    print("2. 检查/创建测试项目...")
    project, created = Project.objects.get_or_create(
        name="API测试项目",
        defaults={'position': 1}
    )
    if created:
        print(f"   ✅ 创建新项目: {project.name}")
    else:
        print(f"   ✅ 使用现有项目: {project.name}")

    # 3. 创建API模块
    print("3. 创建API模块...")
    module = ApiModule.objects.create(
        name="测试API模块",
        project=project,
        module_related=[]
    )
    print(f"   ✅ 创建API模块: {module.name} (ID: {module.id})")

    # 4. 创建API数据
    print("4. 创建API数据...")
    api = ApiData.objects.create(
        name="测试API接口",
        path="/api/test",
        method="GET",
        status=WAITING,
        project=project,
        default_params={"test": "value"},
        timeout=30,
        module=module,
        source=USER_API,
        creater=user
    )
    print(f"   ✅ 创建API数据: {api.name} (ID: {api.id})")

    # 5. 创建API用例模块
    print("5. 创建API用例模块...")
    case_module = ApiCaseModule.objects.create(
        name="测试用例模块",
        position=1
    )
    print(f"   ✅ 创建用例模块: {case_module.name} (ID: {case_module.id})")

    # 6. 创建API测试用例
    print("6. 创建API测试用例...")
    case = ApiCase.objects.create(
        name="测试用例",
        module=case_module,
        status=WAITING,
        remark="这是一个测试用例",
        is_deleted=False,
        position=1,
        creater=user
    )
    print(f"   ✅ 创建API用例: {case.name} (ID: {case.id})")

    # 7. 创建API用例步骤
    print("7. 创建API用例步骤...")
    step = ApiCaseStep.objects.create(
        step_name="测试步骤",
        type="api",
        status=WAITING,
        params={"request_type": "json"},
        api=api,
        enabled=True,
        case=case
    )
    print(f"   ✅ 创建用例步骤: {step.step_name} (ID: {step.id})")

    print("\n✅ 所有数据创建成功!")

    # 验证数据
    print("\n验证插入的数据:")
    print(f"- 用户总数: {LimUser.objects.count()}")
    print(f"- 项目总数: {Project.objects.count()}")
    print(f"- API模块总数: {ApiModule.objects.count()}")
    print(f"- API数据总数: {ApiData.objects.count()}")
    print(f"- API用例模块总数: {ApiCaseModule.objects.count()}")
    print(f"- API用例总数: {ApiCase.objects.count()}")
    print(f"- API用例步骤总数: {ApiCaseStep.objects.count()}")

except Exception as e:
    print(f"\n❌ 错误: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n测试完成!")
