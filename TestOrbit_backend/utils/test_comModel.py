import unittest
from django.test import SimpleTestCase
from utils.comModel import ComModuleModel, ComTimeModel, ProjectModel

class ComModelTest(SimpleTestCase):
    """测试通用模型定义"""
    
    def test_json_field_default_value(self):
        """测试 JSONField 默认值是否正确"""
        # 验证 module_related 字段的默认值是一个可调用对象，而不是一个实例
        field = ComModuleModel._meta.get_field('module_related')
        self.assertTrue(callable(field.default))
        self.assertEqual(field.default, list)
        
        # 由于不能实例化抽象模型，我们只能测试字段的定义
        # 但我们可以验证 JSONField 的默认值是 list 函数而不是 [] 实例
        self.assertIsNot(field.default(), [])
        self.assertEqual(field.default(), [])

class ProjectModelTest(SimpleTestCase):
    """测试 ProjectModel 定义"""
    
    def test_project_model_fields(self):
        """测试 ProjectModel 字段定义"""
        # 验证 id 字段
        id_field = ProjectModel._meta.get_field('id')
        self.assertTrue(id_field.primary_key)
        self.assertEqual(id_field.__class__.__name__, 'SmallAutoField')
        
        # 验证 name 字段
        name_field = ProjectModel._meta.get_field('name')
        self.assertEqual(name_field.max_length, 100)
        self.assertEqual(name_field.verbose_name, '名称')
        
        # 验证 position 字段
        position_field = ProjectModel._meta.get_field('position')
        self.assertEqual(position_field.default, 1)
        self.assertEqual(position_field.verbose_name, '排序')
    
    def test_project_model_meta(self):
        """测试 ProjectModel 元数据"""
        self.assertTrue(ProjectModel._meta.abstract)
        self.assertEqual(ProjectModel._meta.verbose_name, '公共字典模型')


if __name__ == '__main__':
    unittest.main()
