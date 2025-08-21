"""
测试数据生成器
用于生成API测试所需的各种测试数据
"""
import os
import sys
import random
from datetime import datetime, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TestOrbit.settings')
import django
django.setup()

# 导入模型
from apiData.models import ApiModule, ApiData, ApiCaseModule, ApiCase, ApiCaseStep
from project.models import Project, ProjectParamType
from config.models import Environment  # 移除 ProjectEnvirData 导入，因为该模型已被删除
from user.models import LimUser
from utils.constant import WAITING, SUCCESS, FAILED, USER_API
from django.db import transaction

class TestDataGenerator:
    """测试数据生成器类"""
    
    def __init__(self):
        self.users = []
        self.projects = []
        self.environments = []
        self.api_modules = []
        self.api_data_list = []
        self.case_modules = []
        self.api_cases = []
        self.case_steps = []
        
    def create_users(self, count=3):
        """创建测试用户"""
        for i in range(count):
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
            self.users.append(user)
        return self.users
        
    def create_projects(self, count=3):
        """创建测试项目"""
        for i in range(count):
            project, created = Project.objects.get_or_create(
                name=f"测试项目{i+1}",
                defaults={'position': i+1}
            )
            self.projects.append(project)
        return self.projects
        
    def create_environments(self, count=3):
        """创建测试环境"""
        for i in range(count):
            env, created = Environment.objects.get_or_create(
                name=f"测试环境{i+1}",
                defaults={
                    'remark': f'这是测试环境{i+1}的备注',
                    'url': f'http://test{i+1}.example.com'  # 直接在 Environment 中设置 URL
                }
            )
            self.environments.append(env)
            
            # 注意：不再需要 ProjectEnvirData，环境现在是独立的，所有项目都可以访问所有环境
        return self.environments
        
    def create_api_modules(self, count=5):
        """创建API模块"""
        with transaction.atomic():
            for i in range(count):
                module = ApiModule.objects.create(
                    name=f"API模块-{i+1}",
                    project=random.choice(self.projects),
                    module_related=[]
                )
                self.api_modules.append(module)
        return self.api_modules
        
    def create_api_data(self, count=5):
        """创建API数据"""
        api_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        with transaction.atomic():
            for i in range(count):
                method = api_methods[i % len(api_methods)]
                api = ApiData.objects.create(
                    name=f"测试接口-{i+1}",
                    path=f"/api/v1/test{i+1}",
                    method=method,
                    status=random.choice([WAITING, SUCCESS, FAILED]),
                    project=random.choice(self.projects),
                    default_params={
                        "headers": {"Content-Type": "application/json"},
                        "params": {f"param{i+1}": f"value{i+1}"}
                    },
                    timeout=random.randint(10, 60),
                    module=random.choice(self.api_modules),
                    source=USER_API,
                    creater=random.choice(self.users)
                )
                self.api_data_list.append(api)
        return self.api_data_list
        
    def create_case_modules(self, count=5):
        """创建API用例模块"""
        with transaction.atomic():
            # 使用时间戳确保ID唯一
            timestamp_suffix = str(int(datetime.now().timestamp()))[-6:]
            for i in range(count):
                unique_id = f"ACM{timestamp_suffix}{str(i+1).zfill(2)}"
                module = ApiCaseModule.objects.create(
                    id=unique_id,
                    name=f"用例模块-{i+1}",
                    position=i+1
                )
                self.case_modules.append(module)
        return self.case_modules
        
    def create_api_cases(self, count=5):
        """创建API测试用例"""
        with transaction.atomic():
            for i in range(count):
                case = ApiCase.objects.create(
                    name=f"测试用例-{i+1}",
                    module=random.choice(self.case_modules),
                    status=random.choice([WAITING, SUCCESS, FAILED]),
                    remark=f"这是第{i+1}个测试用例的说明",
                    is_deleted=False,
                    latest_run_time=datetime.now() - timedelta(days=random.randint(0, 10)),
                    position=i+1,
                    creater=random.choice(self.users)
                )
                self.api_cases.append(case)
        return self.api_cases
        
    def create_case_steps(self, count=5):
        """创建API用例步骤"""
        with transaction.atomic():
            for i in range(count):
                step = ApiCaseStep.objects.create(
                    step_name=f"测试步骤-{i+1}",
                    type="api",
                    status=random.choice([WAITING, SUCCESS, FAILED]),
                    params={
                        "request_type": "json",
                        "data": {f"key{i+1}": f"value{i+1}"}
                    },
                    api=random.choice(self.api_data_list),
                    enabled=True,
                    controller_data=None,
                    quote_case=None,
                    retried_times=0,
                    case=random.choice(self.api_cases),
                    results=None
                )
                self.case_steps.append(step)
        return self.case_steps
        
    def generate_all_test_data(self, verbose=True):
        """生成所有测试数据"""
        if verbose:
            print("\n" + "="*80)
            print(" "*30 + "生成测试数据")
            print("="*80)
        
        try:
            # 1. 创建基础数据
            if verbose:
                print("\n1. 准备基础数据...")
            
            self.create_users(3)
            if verbose:
                print(f"   准备了 {len(self.users)} 个测试用户")
            
            self.create_projects(3)
            if verbose:
                print(f"   准备了 {len(self.projects)} 个测试项目")
            
            self.create_environments(2)
            if verbose:
                print(f"   准备了 {len(self.environments)} 个测试环境")
            
            # 2. 创建API相关数据
            if verbose:
                print("\n2. 创建API模块...")
            self.create_api_modules()
            if verbose:
                for module in self.api_modules:
                    print(f"   ✅ 创建: {module.name} (ID: {module.id})")
            
            if verbose:
                print("\n3. 创建API数据...")
            self.create_api_data()
            if verbose:
                for api in self.api_data_list:
                    print(f"   ✅ 创建: {api.name} ({api.method} {api.path})")
            
            if verbose:
                print("\n4. 创建API用例模块...")
            self.create_case_modules()
            if verbose:
                for module in self.case_modules:
                    print(f"   ✅ 创建: {module.name} (ID: {module.id})")
            
            if verbose:
                print("\n5. 创建API测试用例...")
            self.create_api_cases()
            if verbose:
                for case in self.api_cases:
                    print(f"   ✅ 创建: {case.name} (模块: {case.module.name})")
            
            if verbose:
                print("\n6. 创建API用例步骤...")
            self.create_case_steps()
            if verbose:
                for step in self.case_steps:
                    print(f"   ✅ 创建: {step.step_name} (用例: {step.case.name})")
            
            if verbose:
                print("\n" + "="*80)
                print(" "*25 + "数据生成完成")
                print("="*80)
                
                # 验证最终数据
                print(f"\n最终数据统计:")
                print(f"- 用户 (LimUser): {LimUser.objects.count()} 条记录")
                print(f"- 项目 (Project): {Project.objects.count()} 条记录")
                print(f"- 环境 (Environment): {Environment.objects.count()} 条记录")
                print(f"- API模块 (ApiModule): {ApiModule.objects.count()} 条记录")
                print(f"- API数据 (ApiData): {ApiData.objects.count()} 条记录")
                print(f"- API用例模块 (ApiCaseModule): {ApiCaseModule.objects.count()} 条记录")
                print(f"- API用例 (ApiCase): {ApiCase.objects.count()} 条记录")
                print(f"- API用例步骤 (ApiCaseStep): {ApiCaseStep.objects.count()} 条记录")
                
                print("\n🎉 所有测试数据生成成功！")
            
            return {
                "users": self.users,
                "projects": self.projects,
                "environments": self.environments,
                "api_modules": self.api_modules,
                "api_data": self.api_data_list,
                "case_modules": self.case_modules,
                "api_cases": self.api_cases,
                "case_steps": self.case_steps
            }
        
        except Exception as e:
            if verbose:
                print(f"\n❌ 错误: {str(e)}")
                import traceback
                traceback.print_exc()
            raise
        
        finally:
            if verbose:
                print("\n" + "="*80)

# 如果直接运行此脚本，生成测试数据
if __name__ == "__main__":
    generator = TestDataGenerator()
    generator.generate_all_test_data()
