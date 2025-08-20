from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from user.models import LimUser
import json

class DatabaseOperationsTests(APITestCase):
    def setUp(self):
        """
        测试前创建测试用户并登录
        """
        self.client = APIClient()
        self.user = LimUser.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)
        
        # 创建测试用的环境配置
        url = '/config/environment-view'
        self.env_data = {
            'name': 'Test Environment',
            'host': 'localhost',
            'port': 3306,
            'username': 'testuser',
            'password': 'testpass',
            'database': 'testdb'
        }
        response = self.client.post(url, self.env_data, format='json')
        self.environment_id = response.data['results']['id']

    def test_run_sql(self):
        """
        测试SQL执行功能
        """
        url = '/config/run-sql'
        data = {
            'environment_id': self.environment_id,
            'sql': 'SELECT 1'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_get_index_statistics(self):
        """
        测试获取索引统计信息
        """
        url = '/config/get-index-statistics'
        data = {
            'environment_id': self.environment_id,
            'database': 'testdb',
            'table': 'test_table'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_sql(self):
        """
        测试执行无效SQL的情况
        """
        url = '/config/run-sql'
        data = {
            'environment_id': self.environment_id,
            'sql': 'INVALID SQL'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_environment(self):
        """
        测试环境配置不存在的情况
        """
        url = '/config/run-sql'
        data = {
            'environment_id': 9999,  # 不存在的环境ID
            'sql': 'SELECT 1'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
