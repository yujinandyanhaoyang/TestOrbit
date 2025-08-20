"""
apiData 应用测试数据生成脚本
为 apiData 应用中的各个模型插入示例测试数据
"""
import os
import sys
import random
from datetime import datetime, timedelta

# 添加父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
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
print(" "*30 + "apiData 测试数据生成")
print("="*80)

# 检查是否已存在数据，避免重复创建
api_module_count = ApiModule.objects.count()
api_data_count = ApiData.objects.count()
api_case_module_count = ApiCaseModule.objects.count()
api_case_count = ApiCase.objects.count()
api_case_step_count = ApiCaseStep.objects.count()

print(f"\n当前数据统计:")
print(f"- ApiModule: {api_module_count} 条记录")
print(f"- ApiData: {api_data_count} 条记录")
print(f"- ApiCaseModule: {api_case_module_count} 条记录")
print(f"- ApiCase: {api_case_count} 条记录") 
print(f"- ApiCaseStep: {api_case_step_count} 条记录")

# 无需交互，直接继续
if any([api_module_count, api_data_count, api_case_module_count, api_case_count, api_case_step_count]):
    print("\n数据库中已存在数据，但我们仍将继续添加示例数据。")

# 准备依赖数据
try:
    # 获取或创建测试用户
    user, created = LimUser.objects.get_or_create(
        username="testadmin",
        defaults={
            'email': 'testadmin@example.com',
            'is_staff': True,
            'is_superuser': True,
            'real_name': '测试管理员'
        }
    )
    if created:
        user.set_password("password123")
        user.save()
        print(f"创建测试用户: {user.username}")
    else:
        print(f"使用现有用户: {user.username}")
    
    # 获取或创建项目
    project, created = Project.objects.get_or_create(
        name="测试项目",
        defaults={'position': 1}
    )
    if created:
        print(f"创建测试项目: {project.name}")
    else:
        print(f"使用现有项目: {project.name}")
    
    # 使用事务来确保数据一致性
    with transaction.atomic():
        # 1. 创建API模块
        api_modules = []
        for i in range(5):
            module = ApiModule.objects.create(
                name=f"API模块{i+1}",
                project=project,
                module_related=[]
            )
            api_modules.append(module)
            print(f"创建API模块: {module.name}")
        
        # 2. 创建API数据
        api_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        api_data_list = []
        for i in range(5):
            method = api_methods[i]
            api = ApiData.objects.create(
                name=f"测试接口{i+1}",
                path=f"/api/test/{i+1}",
                method=method,
                status=random.choice([WAITING, SUCCESS, FAILED]),
                project=project,
                default_params={
                    "headers": {"Content-Type": "application/json"},
                    "params": {"param1": "value1", "param2": "value2"}
                },
                timeout=30,
                module=random.choice(api_modules),
                source=USER_API,
                creater=user
            )
            api_data_list.append(api)
            print(f"创建API数据: {api.name} ({api.method})")
        
        # 3. 创建API用例模块
        case_modules = []
        for i in range(5):
            module = ApiCaseModule.objects.create(
                name=f"用例模块{i+1}",
                position=i+1
            )
            case_modules.append(module)
            print(f"创建用例模块: {module.name}")
        
        # 4. 创建API测试用例
        api_cases = []
        for i in range(5):
            case = ApiCase.objects.create(
                name=f"测试用例{i+1}",
                module=case_modules[i],
                status=random.choice([WAITING, SUCCESS, FAILED]),
                remark=f"这是测试用例{i+1}的说明",
                report_data=None,
                is_deleted=False,
                latest_run_time=datetime.now() - timedelta(days=random.randint(0, 10)),
                position=i+1,
                creater=user
            )
            api_cases.append(case)
            print(f"创建API用例: {case.name}")
        
        # 5. 创建API用例步骤
        for i in range(5):
            case = random.choice(api_cases)
            api = random.choice(api_data_list)
            step = ApiCaseStep.objects.create(
                step_name=f"步骤{i+1}",
                type="api",
                status=random.choice([WAITING, SUCCESS, FAILED]),
                params={
                    "request_type": "json",
                    "data": {"key1": "value1", "key2": "value2"}
                },
                api=api,
                enabled=True,
                controller_data=None,
                quote_case=None,
                retried_times=0,
                case=case,
                results=None
            )
            print(f"创建用例步骤: {step.step_name} (用例: {case.name})")
        
    print("\n" + "="*80)
    print(" "*25 + "测试数据生成完成")
    print("="*80)
    
    # 显示最终数据统计
    print(f"\n最终数据统计:")
    print(f"- ApiModule: {ApiModule.objects.count()} 条记录")
    print(f"- ApiData: {ApiData.objects.count()} 条记录") 
    print(f"- ApiCaseModule: {ApiCaseModule.objects.count()} 条记录")
    print(f"- ApiCase: {ApiCase.objects.count()} 条记录")
    print(f"- ApiCaseStep: {ApiCaseStep.objects.count()} 条记录")
    
except Exception as e:
    print(f"\n❌ 错误: {str(e)}")
    print("数据生成失败。")
