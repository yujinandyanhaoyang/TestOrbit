"""
集成测试：测试各应用之间的交互和数据流
"""
import unittest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

# 导入所有需要的模型
from project.models import Project, ProjectParamType
from config.models import Environment  # 移除 ProjectEnvirData 导入，因为该模型已被删除
from apiData.models import ApiModule, ApiData, ApiCaseModule, ApiCase, ApiCaseStep
from user.models import LimUser
from utils.constant import WAITING

class CrossAppIntegrationTest(TestCase):
    """测试不同应用之间的集成"""
    
    def setUp(self):
        """创建测试数据"""
        # 创建测试用户
        self.user = LimUser.objects.create_user(
            username="testuser", 
            password="password123",
            email="testuser@example.com",
            is_staff=True
        )
        self.client.login(username="testuser", password="password123")
        
        # 创建测试项目
        self.project = Project.objects.create(
            name="集成测试项目",
            position=1
        )
        
        # 创建测试环境（现在直接包含 URL 信息）
        self.environment = Environment.objects.create(
            name="集成测试环境",
            remark="用于集成测试的环境",
            url="http://test.example.com"  # 直接在 Environment 中存储 URL
        )
        
        # 注意：不再需要 ProjectEnvirData，环境数据直接存储在 Environment 模型中
        
        # 创建API模块
        self.api_module = ApiModule.objects.create(
            name="集成测试模块",
            project=self.project,
            module_related=[]
        )
        
        # 创建API数据
        self.api_data = ApiData.objects.create(
            name="集成测试API",
            path="/api/integration-test",
            method="GET",
            status=WAITING,
            project=self.project,
            default_params={
                "headers": {"Content-Type": "application/json"},
                "params": {"test": "value"}
            },
            module=self.api_module,
            creater=self.user
        )
        
        # 创建API用例模块
        self.case_module = ApiCaseModule.objects.create(
            id="ACMINT001",
            name="集成测试用例模块",
            position=1
        )
        
        # 创建API用例
        self.api_case = ApiCase.objects.create(
            name="集成测试用例",
            module=self.case_module,
            status=WAITING,
            remark="集成测试用例说明",
            position=1,
            creater=self.user
        )
        
        # 创建API用例步骤
        self.case_step = ApiCaseStep.objects.create(
            step_name="集成测试步骤",
            type="api",
            status=WAITING,
            params={
                "request_type": "json",
                "data": {"key": "value"}
            },
            api=self.api_data,
            enabled=True,
            case=self.api_case
        )
    
    def test_project_environment_integration(self):
        """测试项目和环境之间的集成"""
        # 验证环境数据正确创建（现在环境是独立的，不再与特定项目绑定）
        self.assertEqual(self.environment.name, "集成测试环境")
        self.assertEqual(self.environment.url, "http://test.example.com")
    
    def test_project_api_integration(self):
        """测试项目和API之间的集成"""
        # 验证API正确关联到项目
        api = ApiData.objects.filter(project=self.project).first()
        self.assertEqual(api, self.api_data)
        self.assertEqual(api.module.project, self.project)
    
    def test_api_case_integration(self):
        """测试API和用例之间的集成"""
        # 验证用例步骤正确关联到API
        step = ApiCaseStep.objects.filter(api=self.api_data).first()
        self.assertEqual(step, self.case_step)
        self.assertEqual(step.case, self.api_case)
    
    def test_user_case_integration(self):
        """测试用户和用例之间的集成"""
        # 验证用例正确关联到创建用户
        case = ApiCase.objects.filter(creater=self.user).first()
        self.assertEqual(case, self.api_case)


class DataFlowIntegrationTest(TestCase):
    """测试数据流在不同应用之间的传递"""
    
    def setUp(self):
        """创建测试数据和关系链"""
        # 设置基础数据
        self.user = LimUser.objects.create_user(
            username="flowuser", 
            password="password123"
        )
        self.client.login(username="flowuser", password="password123")
        
        self.project = Project.objects.create(name="数据流项目")
        self.environment = Environment.objects.create(
            name="数据流环境",
            url="https://api.example.com:443"  # 直接在 Environment 中存储 URL 信息
        )
        
        # 注意：不再需要 ProjectEnvirData，环境数据直接存储在 Environment 模型中
        
        # 创建API模块
        self.api_module = ApiModule.objects.create(
            name="数据流模块",
            project=self.project
        )
        
        # 创建API
        self.api = ApiData.objects.create(
            name="数据流API",
            path="/api/data",
            method="GET",
            project=self.project,
            module=self.api_module,
            creater=self.user,
            default_params={
                "headers": {"Content-Type": "application/json"},
                "params": {"filter": "all"}
            }
        )
        
        # 创建用例模块
        self.case_module = ApiCaseModule.objects.create(
            id="ACMFLOW1",
            name="数据流用例模块"
        )
        
        # 创建用例
        self.case = ApiCase.objects.create(
            name="数据流测试用例",
            module=self.case_module,
            creater=self.user
        )
        
        # 创建用例步骤
        self.step = ApiCaseStep.objects.create(
            step_name="数据流步骤",
            type="api",
            case=self.case,
            api=self.api,
            params={
                "request_type": "json",
                "data": {"id": 1}
            }
        )
    
    def test_complete_data_flow(self):
        """测试完整的数据流：从项目/环境到API到用例执行"""
        # 验证整个数据链
        self.assertEqual(self.step.api.project, self.project)
        self.assertEqual(self.step.api.module.project, self.project)
        self.assertEqual(self.step.case.creater, self.user)
        
        # 验证环境数据可以用于API执行（现在直接从 Environment 获取）
        api = self.step.api
        
        # 模拟数据流：环境数据 + API数据 -> API执行
        # 现在环境 URL 直接存储在 Environment.url 字段中
        execution_data = {
            "base_url": self.environment.url,  # 直接从 Environment 获取 URL
            "path": api.path,
            "method": api.method,
            "headers": api.default_params.get("headers", {}),
            "params": {**api.default_params.get("params", {}), **self.step.params.get("data", {})}
        }
        
        # 验证数据流组装结果
        self.assertEqual(execution_data["host"], "api.example.com")
        self.assertEqual(execution_data["path"], "/api/data")
        self.assertEqual(execution_data["method"], "GET")
        self.assertEqual(execution_data["params"]["filter"], "all")
        self.assertEqual(execution_data["params"]["id"], 1)


if __name__ == '__main__':
    unittest.main()
