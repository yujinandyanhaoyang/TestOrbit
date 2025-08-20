"""
apiData 接口可用性测试脚本
验证通过 API 访问和操作测试数据的能力
"""
import os
import sys
import requests
import json
from datetime import datetime

# 添加父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TestOrbit.settings')
import django
django.setup()

# 导入模型
from user.models import LimUser
from project.models import Project
from apiData.models import ApiModule, ApiData, ApiCaseModule, ApiCase, ApiCaseStep

class ApiTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"  # 修改为你的实际服务器地址
        self.token = None
        self.user = None
        self.headers = {"Content-Type": "application/json"}
    
    def login(self):
        """登录并获取认证令牌"""
        print("\n登录系统...")
        
        # 获取或创建测试用户
        try:
            self.user = LimUser.objects.get(username="testadmin")
        except LimUser.DoesNotExist:
            print("错误: 测试用户不存在，请先运行 generate_test_data.py 创建测试数据")
            sys.exit(1)
        
        # 获取令牌
        url = f"{self.base_url}/user/login"
        data = {
            "username": "testadmin",
            "password": "password123"
        }
        
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200 and response.json()['token']:
                self.token = response.json()['token']
                self.headers["Authorization"] = f"Token {self.token}"
                print(f"✅ 登录成功! 用户: {self.user.username}")
                return True
            else:
                print(f"❌ 登录失败: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 登录请求异常: {str(e)}")
            return False
    
    def test_get_api_modules(self):
        """测试获取API模块"""
        print("\n测试获取API模块...")
        url = f"{self.base_url}/api-data/module-view"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                modules = response.json()['results']
                print(f"✅ 成功获取 {len(modules)} 个API模块")
                for module in modules[:3]:  # 只显示前3个
                    print(f"  - {module['name']}")
                return True
            else:
                print(f"❌ 获取API模块失败: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 请求异常: {str(e)}")
            return False
    
    def test_get_api_data(self):
        """测试获取API数据"""
        print("\n测试获取API数据...")
        url = f"{self.base_url}/api-data/api-view"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                apis = response.json()['results']
                print(f"✅ 成功获取 {len(apis)} 个API数据")
                for api in apis[:3]:  # 只显示前3个
                    print(f"  - {api['name']} ({api['method']}: {api['path']})")
                return True
            else:
                print(f"❌ 获取API数据失败: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 请求异常: {str(e)}")
            return False
    
    def test_get_api_cases(self):
        """测试获取API测试用例"""
        print("\n测试获取API测试用例...")
        url = f"{self.base_url}/api-data/api-case-list"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                cases = response.json()['data']
                print(f"✅ 成功获取 {len(cases)} 个API测试用例")
                for case in cases[:3]:  # 只显示前3个
                    print(f"  - {case['name']}")
                return True
            else:
                print(f"❌ 获取API测试用例失败: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 请求异常: {str(e)}")
            return False
    
    def test_create_api_module(self):
        """测试创建API模块"""
        print("\n测试创建API模块...")
        url = f"{self.base_url}/api-data/module-view"
        
        # 获取项目
        try:
            project = Project.objects.get(name="测试项目")
        except Project.DoesNotExist:
            print("错误: 测试项目不存在，请先运行 generate_test_data.py 创建测试数据")
            return False
        
        data = {
            "name": f"新API模块-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "project_id": project.id,
            "position": 99,
            "module_related": []
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code == 201:
                print(f"✅ 成功创建API模块: {data['name']}")
                return True
            else:
                print(f"❌ 创建API模块失败: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 请求异常: {str(e)}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*80)
        print(" "*30 + "apiData API 可用性测试")
        print("="*80)
        
        # 先登录
        if not self.login():
            return False
        
        # 运行所有测试
        tests = [
            self.test_get_api_modules,
            self.test_get_api_data,
            self.test_get_api_cases,
            self.test_create_api_module
        ]
        
        results = []
        for test in tests:
            result = test()
            results.append((test.__name__, result))
        
        # 显示测试结果
        print("\n" + "="*80)
        print(" "*30 + "测试结果汇总")
        print("="*80)
        
        all_passed = True
        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name}: {status}")
            if not result:
                all_passed = False
        
        if all_passed:
            print("\n🎉 所有测试都通过了! 系统功能正常。")
        else:
            print("\n⚠️ 部分测试失败，请检查系统功能。")
        
        return all_passed

if __name__ == "__main__":
    tester = ApiTester()
    tester.run_all_tests()
