import unittest
from django.test import TestCase, SimpleTestCase
from project.models import Project, ProjectParamType


class ProjectModelMappingTest(SimpleTestCase):
    """测试 Project 模型映射到正确的数据库表"""
    
    def test_project_table_mapping(self):
        """验证 Project 模型映射到 'project' 表"""
        # 验证模型元数据
        self.assertEqual(Project._meta.db_table, 'project')
    
    def test_project_fields_mapping(self):
        """验证 Project 模型的字段映射正确"""
        # 验证关键字段
        name_field = Project._meta.get_field('name')
        self.assertTrue(name_field.unique)
        self.assertEqual(name_field.max_length, 100)
        
        # 验证时间字段存在且设置正确
        created_field = Project._meta.get_field('created')
        self.assertTrue(created_field.auto_now_add)
        
        updated_field = Project._meta.get_field('updated')
        self.assertTrue(updated_field.auto_now)
        
    def test_param_type_table_mapping(self):
        """验证 ProjectParamType 模型映射到 'project_param_type' 表"""
        # 验证模型元数据
        self.assertEqual(ProjectParamType._meta.db_table, 'project_param_type')


if __name__ == '__main__':
    unittest.main()
