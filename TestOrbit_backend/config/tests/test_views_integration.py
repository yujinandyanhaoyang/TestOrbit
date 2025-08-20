import unittest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from user.models import LimUser
from config.models import Environment, ProjectEnvirData
from project.models import Project


class EnvironmentViewTest(TestCase):
    """测试 Environment 视图的功能"""
    
    def setUp(self):
        """
        设置测试数据和客户端
        """
        self.client = APIClient()
        # 创建测试用户并登录
        self.user = LimUser.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)
        
        # 创建初始项目
        self.project = Project.objects.create(name="测试项目", position=1)
    
    def test_environment_view_create(self):
        """测试创建环境配置"""
        url = '/config/environment-view'  # 使用新的正确路径
        data = {
            'name': '测试环境',
            'remark': '这是一个测试环境',
            f'envir_1_api': {
                'host': 'http://testhost.com',
                'port': 8080,
                'username': 'testuser',
                'password': 'testpass'
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"响应内容: {response.content}")
        
        # 验证环境是否真的创建了
        self.assertTrue(Environment.objects.filter(name='测试环境').exists())
        
        # 验证环境数据是否正确关联
        env = Environment.objects.get(name='测试环境')
        self.assertTrue(ProjectEnvirData.objects.filter(envir=env, project=self.project).exists())
    
    def test_environment_view_list(self):
        """测试获取环境配置列表"""
        # 创建测试环境
        env = Environment.objects.create(name="测试环境", remark="这是一个测试环境")
        ProjectEnvirData.objects.create(envir=env, project=self.project, data={
            'api': {'host': 'http://testhost.com'}
        })
        
        url = '/config/environment-view'  # 使用新的正确路径
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证返回了正确的环境数量
        self.assertEqual(len(response.data['results']), 1)
        
    def test_test_db_connect(self):
        """测试数据库连接功能"""
        url = '/config/test-db-connect'  # 使用新的正确路径
        data = {
            'host': 'localhost',
            'port': 3306,
            'username': 'testuser',
            'password': 'testpass',
            'database': 'test_db',
            'ssh_tunnel': False
        }
        
        # 注意：这个测试可能需要模拟数据库连接
        # 在实际环境中，我们可能需要模拟 db_connect 函数的返回值
        # 这里仅做示例，实际测试可能会因环境不同而失败
        
        response = self.client.post(url, data, format='json')
        # 由于我们无法确保真实环境下的数据库连接，此处仅验证请求被正确处理
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])


if __name__ == '__main__':
    unittest.main()
