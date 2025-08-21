from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from config.models import Environment  # 移除 ProjectEnvirData 导入
from apiData.models import ApiModule


class EnvironmentViewTests(TestCase):
    def setUp(self):
        """
        测试前的准备工作
        """
        self.client = APIClient()
        self.url = reverse('config:env-view')  # 使用URL名称而不是硬编码的路径

    def test_create_environment(self):
        """
        测试创建环境的功能
        """
        # 准备测试数据
        test_data = {
            'name': '测试环境',
            'remark': '这是一个测试环境',
            'url': 'http://test.example.com',
            # 添加环境配置数据
            'envir_1_api': 'http://api.test.com',
            'envir_1_db': [
                {
                    'db_con_name': 'default',
                    'host': 'localhost',
                    'port': 3306,
                    'username': 'test',
                    'password': 'test123'
                }
            ]
        }

        # 发送POST请求
        response = self.client.post(self.url, test_data, format='json')

        # 验证响应状态码
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['msg'], '创建成功！')

        # 验证数据库中是否正确创建了环境
        created_env = Environment.objects.filter(name='测试环境').first()
        self.assertIsNotNone(created_env)
        self.assertEqual(created_env.remark, '这是一个测试环境')
        self.assertEqual(created_env.url, 'http://test.example.com')

        # 在新的实现中，不再需要验证 ProjectEnvirData，直接从 Environment 中获取 URL
        # URL 现在直接保存在 Environment 表的 url 字段中

        # 注意：环境创建时不再自动创建 ApiModule，因为环境应该独立于特定项目
        # 如果需要为特定项目创建模块，应该在项目管理中进行

    def test_create_duplicate_environment(self):
        """
        测试创建同名环境的情况
        """
        # 先创建一个环境
        Environment.objects.create(
            name='测试环境',
            remark='原始环境',
            url='http://original.example.com'
        )

        # 尝试创建同名环境
        test_data = {
            'name': '测试环境',  # 使用相同的名称
            'remark': '这是一个重复的测试环境',
            'url': 'http://duplicate.example.com'
        }

        # 发送POST请求
        response = self.client.post(self.url, test_data, format='json')

        # 验证是否返回400错误
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('已存在同名环境', response.data['msg'])

    def test_create_environment_without_required_fields(self):
        """
        测试缺少必填字段的情况
        """
        # 准备缺少name的测试数据
        test_data = {
            'remark': '这是一个测试环境',
            'url': 'http://test.example.com'
        }

        # 发送POST请求
        response = self.client.post(self.url, test_data, format='json')

        # 验证是否返回400错误
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def tearDown(self):
        """
        测试后的清理工作
        """
        # 清理测试数据
        Environment.objects.all().delete()
        # ProjectEnvirData 模型已被删除，不再需要清理
        ApiModule.objects.all().delete()
