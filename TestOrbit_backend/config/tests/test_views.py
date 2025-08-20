from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from user.models import LimUser

class EnvironmentViewTests(APITestCase):
    def setUp(self):
        """
        测试前创建测试用户并登录
        """
        self.client = APIClient()
        # 创建测试用户
        self.user = LimUser.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        # 登录
        self.client.force_authenticate(user=self.user)

    def test_environment_view_create(self):
        """
        测试创建环境配置
        """
        # 直接使用路径，因为在urls.py中没有命名URL模式
        url = '/config/environment-view'
        data = {
            'name': 'Test Environment',
            'host': 'localhost',
            'port': 3306,
            'username': 'testuser',
            'password': 'testpass',
            'database': 'testdb'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], True)

    def test_environment_view_list(self):
        """
        测试获取环境配置列表
        """
        url = '/config/environment-view'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

class EnvironmentOverviewTests(APITestCase):
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

    def test_environment_overview(self):
        """
        测试获取环境概览
        """
        url = '/config/environment-overview'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

class DatabaseConnectionTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = LimUser.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)

    def test_database_connection(self):
        """
        测试数据库连接
        """
        url = '/config/test-db-connect'
        data = {
            'host': 'localhost',
            'port': 3306,
            'username': 'testuser',
            'password': 'testpass',
            'database': 'testdb'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_databases(self):
        """
        测试获取数据库列表
        """
        url = '/config/proj-db-database'
        data = {
            'host': 'localhost',
            'port': 3306,
            'username': 'testuser',
            'password': 'testpass'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
