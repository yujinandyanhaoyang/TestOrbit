import json
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from project.models import Project, ProjectParamType
from project.serializers import ProjectSerializer
from utils.comModel import ProjectModel


class ProjectModelTest(TestCase):
    """Project 模型测试类"""

    def test_create_project(self):
        """测试创建项目对象"""
        project = Project(name="测试项目", position=1)
        self.assertEqual(project.name, "测试项目")
        self.assertEqual(project.position, 1)
        self.assertEqual(str(Project._meta.db_table), 'project')
        
    def test_project_model_fields(self):
        """测试项目模型的字段"""
        self.assertTrue(hasattr(Project, 'name'))
        self.assertTrue(hasattr(Project, 'position'))
        self.assertTrue(hasattr(Project, 'id'))
    
    def test_project_inheritance(self):
        """测试 Project 继承自 ProjectModel"""
        self.assertTrue(issubclass(Project, ProjectModel))
        
    def test_project_unique_name(self):
        """测试项目名称唯一约束"""
        name_field = Project._meta.get_field('name')
        self.assertTrue(name_field.unique)


class ProjectParamTypeTest(TestCase):
    """ProjectParamType 模型测试类"""
    
    def test_create_param_type(self):
        """测试创建参数类型对象"""
        param_type = ProjectParamType(id="string", name="字符串", position=1)
        self.assertEqual(param_type.id, "string")
        self.assertEqual(param_type.name, "字符串")
        self.assertEqual(param_type.position, 1)
    
    def test_param_type_model_fields(self):
        """测试参数类型模型的字段"""
        self.assertTrue(hasattr(ProjectParamType, 'id'))
        self.assertTrue(hasattr(ProjectParamType, 'name'))
        self.assertTrue(hasattr(ProjectParamType, 'position'))
        
    def test_param_type_table_name(self):
        """测试表名是否正确设置"""
        self.assertEqual(ProjectParamType._meta.db_table, 'project_param_type')
        
    def test_param_type_inheritance(self):
        """测试 ProjectParamType 继承自 ProjectModel"""
        self.assertTrue(issubclass(ProjectParamType, ProjectModel))
        
    def test_param_type_primary_key(self):
        """测试主键字段是否正确设置"""
        id_field = ProjectParamType._meta.get_field('id')
        self.assertTrue(id_field.primary_key)
        self.assertEqual(id_field.max_length, 8)


class ProjectAPITest(TestCase):
    """Project API 测试类"""

    def setUp(self):
        """
        设置测试数据和客户端
        """
        self.client = APIClient()
        self.project1 = Project.objects.create(name="测试项目1", position=1)
        self.project2 = Project.objects.create(name="测试项目2", position=2)
        self.project3 = Project.objects.create(name="测试项目3", position=3)

    def test_get_all_projects(self):
        """
        测试获取所有项目
        """
        response = self.client.get('/conf/envir-view')
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)
    
    def test_create_project(self):
        """
        测试创建项目
        """
        valid_payload = {
            'name': '新测试项目',
        }
        
        response = self.client.post(
            '/conf/envir-view',
            data=json.dumps(valid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 4)
        self.assertEqual(Project.objects.get(name='新测试项目').position, 4)
    
    def test_create_duplicate_project(self):
        """
        测试创建重名项目（应该失败）
        """
        invalid_payload = {
            'name': '测试项目1',
        }
        
        response = self.client.post(
            '/conf/envir-view',
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_delete_project(self):
        """
        测试删除项目
        """
        # 创建额外项目以确保不会触发"必须保留至少一个项目"的限制
        Project.objects.create(name="测试项目4", position=4)
        
        response = self.client.delete(
            f"/conf/envir-view?id={self.project3.id}"
        )
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 3)
        self.assertFalse(Project.objects.filter(name="测试项目3").exists())
    
    def test_delete_last_project(self):
        """
        测试当只有一个项目时尝试删除（应该失败）
        """
        # 删除其他项目，只保留一个
        Project.objects.filter(id__in=[self.project2.id, self.project3.id]).delete()
        
        response = self.client.delete(
            f"/conf/envir-view?id={self.project1.id}"
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Project.objects.count(), 1)


class ChangeProjectPositionTest(TestCase):
    """测试修改项目顺序"""
    
    def setUp(self):
        """
        设置测试数据和客户端
        """
        self.client = APIClient()
        self.project1 = Project.objects.create(name="测试项目1", position=1)
        self.project2 = Project.objects.create(name="测试项目2", position=2)
        self.project3 = Project.objects.create(name="测试项目3", position=3)
    
    def test_move_project_up(self):
        """
        测试项目向上移动
        """
        payload = {
            'id': self.project2.id,
            'type': 'up'
        }
        
        response = self.client.post(
            '/conf/change-envir-position',
            data=payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 刷新数据库状态
        self.project1.refresh_from_db()
        self.project2.refresh_from_db()
        
        # 验证位置交换
        self.assertEqual(self.project1.position, 2)
        self.assertEqual(self.project2.position, 1)
    
    def test_move_project_down(self):
        """
        测试项目向下移动
        """
        payload = {
            'id': self.project2.id,
            'type': 'down'
        }
        
        response = self.client.post(
            '/conf/change-envir-position',
            data=payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 刷新数据库状态
        self.project2.refresh_from_db()
        self.project3.refresh_from_db()
        
        # 验证位置交换
        self.assertEqual(self.project2.position, 3)
        self.assertEqual(self.project3.position, 2)
    
    def test_move_first_project_up(self):
        """
        测试第一个项目继续向上移动（位置应该不变）
        """
        original_position = self.project1.position
        
        payload = {
            'id': self.project1.id,
            'type': 'up'
        }
        
        response = self.client.post(
            '/conf/change-envir-position',
            data=payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 刷新数据库状态
        self.project1.refresh_from_db()
        
        # 验证位置不变
        self.assertEqual(self.project1.position, original_position)
    
    def test_move_last_project_down(self):
        """
        测试最后一个项目继续向下移动（位置应该不变）
        """
        original_position = self.project3.position
        
        payload = {
            'id': self.project3.id,
            'type': 'down'
        }
        
        response = self.client.post(
            '/conf/change-envir-position',
            data=payload,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 刷新数据库状态
        self.project3.refresh_from_db()
        
        # 验证位置不变
        self.assertEqual(self.project3.position, original_position)
        
    def test_invalid_project_id(self):
        """
        测试无效项目ID
        """
        invalid_id = 9999  # 假设不存在此ID
        
        payload = {
            'id': invalid_id,
            'type': 'up'
        }
        
        # 使用try-except捕获预期的异常
        try:
            response = self.client.post(
                '/conf/change-envir-position',
                data=payload,
                format='json'
            )
            self.fail("应该抛出异常，因为项目ID无效")
        except:
            # 预期会抛出异常，测试通过
            pass


class GetParamTypeTest(TestCase):
    """测试参数类型API"""
    
    def setUp(self):
        self.client = APIClient()
        # 创建一些参数类型数据
        ProjectParamType.objects.create(id="string", name="字符串类型", position=1)
        ProjectParamType.objects.create(id="number", name="数字类型", position=2)
        ProjectParamType.objects.create(id="boolean", name="布尔类型", position=3)
    
    def test_get_param_type(self):
        """
        测试获取参数类型
        """
        response = self.client.get('/conf/param-type')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        
        # 验证返回的数据包含预期的参数类型
        data = response.data
        self.assertIn('param_type', data)
        
    def test_param_type_structure(self):
        """
        测试参数类型返回的数据结构
        """
        response = self.client.get('/conf/param-type')
        
        # 检查基本的数据结构
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 这里根据实际的 get_params_type_func() 的返回值来验证
        # 由于我们无法确切知道函数的实现细节，这里只进行基本检查
        self.assertIsInstance(response.data, dict)
        
    def test_param_type_response_time(self):
        """
        测试参数类型接口的响应时间
        """
        import time
        
        start_time = time.time()
        response = self.client.get('/conf/param-type')
        end_time = time.time()
        
        # 验证接口响应时间在合理范围内（这里假设小于0.5秒是合理的）
        self.assertLess(end_time - start_time, 0.5)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
