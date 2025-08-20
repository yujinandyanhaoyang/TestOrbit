import unittest
from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase  # 不依赖数据库
from django.http import HttpRequest
from rest_framework.test import APIRequestFactory

from project.models import Project
from project.views import ProjectView

class ProjectViewPostTest(SimpleTestCase):
    """测试 ProjectView 的 post 方法"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = ProjectView.as_view()

    @patch('project.views.Project.objects.aggregate')
    @patch('project.views.ProjectView.create')
    def test_post_method_removes_creater(self, mock_create, mock_aggregate):
        # 设置 aggregate 的返回值
        mock_aggregate.return_value = {'position__max': 3}
        
        # 设置 create 的返回值
        mock_response = MagicMock()
        mock_create.return_value = mock_response
        
        # 创建请求
        request = self.factory.post('/conf/envir-view', {'name': '测试项目'}, format='json')
        request.user = MagicMock()
        
        # 添加 creater 字段模拟 LimView 的行为
        request.data['creater'] = request.user.id
        
        # 调用视图
        response = self.view(request)
        
        # 验证 create 方法的调用
        mock_create.assert_called_once()
        
        # 验证 creater 字段已被移除
        self.assertNotIn('creater', request.data)
        
        # 验证 position 字段已被设置
        self.assertEqual(request.data['position'], 4)

if __name__ == '__main__':
    unittest.main()
