import unittest
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from project.models import Project
from user.models import LimUser


class ProjectViewTest(TestCase):
    """测试 Project 视图的功能"""
    
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
        self.project1 = Project.objects.create(name="测试项目1", position=1)
        
    def test_project_view_create(self):
        """测试创建项目"""
        url = '/project/project-view'  # 注意：这里使用的URL应该是新的正确路径
        data = {
            'name': '新测试项目',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, f"响应内容: {response.content}")
        
        # 验证项目是否真的创建了
        self.assertTrue(Project.objects.filter(name='新测试项目').exists())
        
        # 验证position是否正确设置
        new_project = Project.objects.get(name='新测试项目')
        self.assertEqual(new_project.position, 2)  # 应该是自增值
    
    def test_project_view_list(self):
        """测试获取项目列表"""
        url = '/project/project-view'  # 使用新的正确路径
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证返回了正确的项目数量
        self.assertEqual(len(response.data['results']), 1)
        
    def test_project_view_delete_with_constraint(self):
        """测试删除唯一项目时的约束"""
        url = f'/project/project-view?id={self.project1.id}'  # 使用新的正确路径
        response = self.client.delete(url)
        
        # 应该失败，因为这是唯一的项目
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('必须保留至少一个项目', response.data.get('msg', ''))
        
        # 验证项目没有被删除
        self.assertTrue(Project.objects.filter(id=self.project1.id).exists())


if __name__ == '__main__':
    unittest.main()
