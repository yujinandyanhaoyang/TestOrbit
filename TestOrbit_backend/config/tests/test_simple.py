from django.test import TestCase, Client
from django.urls import reverse
import json

class SimpleTest(TestCase):
    def test_config_urls_exist(self):
        """
        测试基本URL是否可访问
        """
        client = Client()
        response = client.get('/config/project-view')
        # 只检查响应状态，不关心内容
        self.assertIn(response.status_code, [200, 302, 401, 403])
        
        response = client.get('/config/project-overview')
        self.assertIn(response.status_code, [200, 302, 401, 403])
        
        print("基本URL测试通过")
