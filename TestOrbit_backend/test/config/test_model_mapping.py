import unittest
from django.test import TestCase, SimpleTestCase
from config.models import Environment, ProjectEnvirData
from project.models import Project


class ConfigModelMappingTest(SimpleTestCase):
    """测试 Environment 和 ProjectEnvirData 模型映射到正确的数据库表"""
    
    def test_environment_table_mapping(self):
        """验证 Environment 模型映射到 'environment' 表"""
        # 验证模型元数据
        self.assertEqual(Environment._meta.db_table, 'environment')
    
    def test_environment_fields_mapping(self):
        """验证 Environment 模型的字段映射正确"""
        # 验证关键字段
        name_field = Environment._meta.get_field('name')
        self.assertTrue(name_field.unique)
        self.assertEqual(name_field.max_length, 32)
        
        # 验证时间字段存在
        self.assertTrue(hasattr(Environment, 'created'))
        self.assertTrue(hasattr(Environment, 'updated'))
        
    def test_project_envir_data_table_mapping(self):
        """验证 ProjectEnvirData 模型映射到 'project_envir_data' 表"""
        # 验证模型元数据
        self.assertEqual(ProjectEnvirData._meta.db_table, 'project_envir_data')
            
    def test_relationships(self):
        """验证模型间的关系映射正确"""
        # 验证 ProjectEnvirData 与 Environment 和 Project 的外键关系
        envir_field = ProjectEnvirData._meta.get_field('envir')
        self.assertEqual(envir_field.related_model, Environment)
        
        project_field = ProjectEnvirData._meta.get_field('project')
        self.assertEqual(project_field.related_model, Project)


if __name__ == '__main__':
    unittest.main()
