import unittest
from django.test import TestCase, Client
from django.urls import reverse, NoReverseMatch


class UrlRoutingTest(TestCase):
    """测试URL路由配置是否正确"""
    
    def setUp(self):
        self.client = Client()
    
    def test_project_urls_exist(self):
        """测试 project 应用的 URL 是否可访问"""
        # 注意：我们不关心认证，只关心路由是否存在
        response = self.client.get('/project/project-view')
        self.assertNotEqual(response.status_code, 404, "project-view URL 应该存在")
        
        response = self.client.get('/project/change-project-position')
        self.assertNotEqual(response.status_code, 404, "change-project-position URL 应该存在")
        
        response = self.client.get('/project/get-param-type')
        self.assertNotEqual(response.status_code, 404, "get-param-type URL 应该存在")
    
    def test_config_urls_exist(self):
        """测试 config 应用的 URL 是否可访问"""
        response = self.client.get('/config/environment-view')
        self.assertNotEqual(response.status_code, 404, "environment-view URL 应该存在")
        
        response = self.client.get('/config/environment-overview')
        self.assertNotEqual(response.status_code, 404, "environment-overview URL 应该存在")
        
        response = self.client.get('/config/test-db-connect')
        self.assertNotEqual(response.status_code, 404, "test-db-connect URL 应该存在")
    
    def test_legacy_urls_redirects(self):
        """测试旧的 URL 路径是否被正确重定向或仍然可访问"""
        # 测试旧的 conf 路径是否仍然可用（可能重定向）
        response = self.client.get('/conf/envir-view', follow=True)
        self.assertNotEqual(response.status_code, 404, "旧的 conf/envir-view 路径应该可访问或重定向")
        
        # 测试旧的 project 路径是否仍然可用（可能重定向）
        response = self.client.get('/project/', follow=True)
        self.assertNotEqual(response.status_code, 404, "旧的 project/ 路径应该可访问或重定向")


if __name__ == '__main__':
    unittest.main()
