import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.http import HttpRequest
from rest_framework.test import APIRequestFactory
from django.utils import timezone

from project.models import Project
from project.views import ProjectView

class ProjectViewMockTest(TestCase):
    """测试 ProjectView 处理 creater 字段和 created 字段的逻辑"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ProjectView()
        
    def test_post_method_handles_fields_correctly(self):
        # 创建模拟请求
        data = {'name': '测试项目', 'creater': 1, 'created': timezone.now()}
        request = self.factory.post('/conf/envir-view', data, format='json')
        
        # 添加 data 属性
        request.data = data
        
        # 模拟 Project.objects.aggregate
        self.view.queryset = MagicMock()
        self.view.queryset.aggregate.return_value = {'position__max': 3}
        
        # 模拟 self.create 方法
        self.view.create = MagicMock()
        
        # 调用 post 方法
        self.view.post(request)
        
        # 验证字段处理
        self.assertNotIn('creater', request.data, "creater字段应该被删除")
        self.assertNotIn('created', request.data, "created字段应该被删除")
        self.assertEqual(request.data['position'], 4, "position字段应该被正确设置")
        
        # 验证 create 方法被调用
        self.view.create.assert_called_once_with(request)

if __name__ == '__main__':
    unittest.main()
