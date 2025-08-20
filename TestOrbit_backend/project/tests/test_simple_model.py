import unittest
from django.test import SimpleTestCase
from project.models import Project


class ProjectModelSimpleTest(SimpleTestCase):
    """Project 模型的简单测试，不使用数据库"""
    
    def test_project_model_attributes(self):
        """测试 Project 模型的属性"""
        # 检查模型的 Meta 属性
        self.assertEqual(Project._meta.verbose_name, '项目配置字典表')
        self.assertEqual(Project._meta.db_table, 'project')
        
        # 检查字段属性
        name_field = Project._meta.get_field('name')
        self.assertTrue(name_field.unique)
        self.assertEqual(name_field.max_length, 100)
        self.assertEqual(name_field.verbose_name, '名称')
        
        # 检查 position 字段
        position_field = Project._meta.get_field('position')
        self.assertEqual(position_field.default, 1)
        self.assertEqual(position_field.verbose_name, '排序')


if __name__ == '__main__':
    unittest.main()
