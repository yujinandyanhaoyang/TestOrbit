"""
apiData 接口可用性测试脚本
验证通过 API 访问和操作测试数据的能力
"""
import os
import sys
import unittest
from django.test import TestCase
import requests
import json
from datetime import datetime

# 导入模型
from user.models import LimUser
from project.models import Project
from apiData.models import ApiModule, ApiData, ApiCaseModule, ApiCase, ApiCaseStep

class ApiDataModelsTest(TestCase):
    """测试 apiData 应用中的模型"""
    
    def setUp(self):
        """创建测试数据"""
        # 创建测试用户
        self.user = LimUser.objects.create_user(
            username="testuser", 
            password="password123",
            email="testuser@example.com"
        )
        
        # 创建测试项目
        self.project = Project.objects.create(name="测试项目")
        
        # 创建API模块
        self.api_module = ApiModule.objects.create(
            name="测试API模块",
            project=self.project
        )
        
        # 创建API数据
        self.api_data = ApiData.objects.create(
            name="测试API",
            path="/api/test",
            method="GET",
            project=self.project,
            module=self.api_module,
            creater=self.user
        )
        
        # 创建API用例模块
        self.case_module = ApiCaseModule.objects.create(
            name="测试用例模块",
            id="ACMTEST001"
        )
        
        # 创建API用例
        self.api_case = ApiCase.objects.create(
            name="测试用例",
            module=self.case_module,
            creater=self.user
        )
        
        # 创建API用例步骤
        self.case_step = ApiCaseStep.objects.create(
            step_name="测试步骤",
            type="api",
            api=self.api_data,
            case=self.api_case
        )
    
    def test_api_module_creation(self):
        """测试API模块创建"""
        self.assertEqual(self.api_module.name, "测试API模块")
        self.assertEqual(self.api_module.project, self.project)
    
    def test_api_data_creation(self):
        """测试API数据创建"""
        self.assertEqual(self.api_data.name, "测试API")
        self.assertEqual(self.api_data.path, "/api/test")
        self.assertEqual(self.api_data.method, "GET")
        self.assertEqual(self.api_data.project, self.project)
        self.assertEqual(self.api_data.module, self.api_module)
        self.assertEqual(self.api_data.creater, self.user)
    
    def test_api_case_module_creation(self):
        """测试API用例模块创建"""
        self.assertEqual(self.case_module.name, "测试用例模块")
        self.assertEqual(self.case_module.id, "ACMTEST001")
    
    def test_api_case_creation(self):
        """测试API用例创建"""
        self.assertEqual(self.api_case.name, "测试用例")
        self.assertEqual(self.api_case.module, self.case_module)
        self.assertEqual(self.api_case.creater, self.user)
    
    def test_api_case_step_creation(self):
        """测试API用例步骤创建"""
        self.assertEqual(self.case_step.step_name, "测试步骤")
        self.assertEqual(self.case_step.type, "api")
        self.assertEqual(self.case_step.api, self.api_data)
        self.assertEqual(self.case_step.case, self.api_case)


class ApiDataRelationshipsTest(TestCase):
    """测试 apiData 应用中的模型关系"""
    
    def setUp(self):
        """创建测试数据和关系"""
        # 创建测试用户
        self.user = LimUser.objects.create_user(
            username="testuser", 
            password="password123",
            email="testuser@example.com"
        )
        
        # 创建测试项目
        self.project = Project.objects.create(name="测试项目")
        
        # 创建API模块及子模块
        self.parent_module = ApiModule.objects.create(
            name="父模块",
            project=self.project
        )
        
        self.child_module = ApiModule.objects.create(
            name="子模块",
            project=self.project
        )
        
        # 设置模块关系
        self.parent_module.module_related = [self.child_module.id]
        self.parent_module.save()
        
        # 创建API数据
        self.api_data = ApiData.objects.create(
            name="测试API",
            path="/api/test",
            method="GET",
            project=self.project,
            module=self.parent_module,
            creater=self.user
        )
        
        # 创建API用例模块
        self.case_module = ApiCaseModule.objects.create(
            name="测试用例模块",
            id="ACMTEST001"
        )
        
        # 创建多个API用例
        self.api_case1 = ApiCase.objects.create(
            name="测试用例1",
            module=self.case_module,
            creater=self.user
        )
        
        self.api_case2 = ApiCase.objects.create(
            name="测试用例2",
            module=self.case_module,
            creater=self.user
        )
        
        # 创建多个步骤
        self.case_step1 = ApiCaseStep.objects.create(
            step_name="测试步骤1",
            type="api",
            api=self.api_data,
            case=self.api_case1
        )
        
        self.case_step2 = ApiCaseStep.objects.create(
            step_name="测试步骤2",
            type="api",
            api=self.api_data,
            case=self.api_case1
        )
    
    def test_module_relationships(self):
        """测试模块之间的关系"""
        self.assertIn(self.child_module.id, self.parent_module.module_related)
    
    def test_api_case_steps(self):
        """测试用例与步骤之间的关系"""
        steps = ApiCaseStep.objects.filter(case=self.api_case1)
        self.assertEqual(steps.count(), 2)
        self.assertEqual(steps[0].step_name, "测试步骤1")
        self.assertEqual(steps[1].step_name, "测试步骤2")
    
    def test_module_api_relationship(self):
        """测试模块与API之间的关系"""
        apis = ApiData.objects.filter(module=self.parent_module)
        self.assertEqual(apis.count(), 1)
        self.assertEqual(apis[0].name, "测试API")
    
    def test_project_api_relationship(self):
        """测试项目与API之间的关系"""
        apis = ApiData.objects.filter(project=self.project)
        self.assertEqual(apis.count(), 1)
        self.assertEqual(apis[0].name, "测试API")


if __name__ == '__main__':
    unittest.main()
