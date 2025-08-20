"""
测试环境配置
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TestOrbit.settings')
django.setup()

# 导入需要测试的模型
from config.models import Environment, ProjectEnvirData
from project.models import Project

# 简单测试: 创建环境实例并验证
try:
    # 创建环境实例
    new_env = Environment(name="测试环境", remark="测试用途")
    
    # 验证属性
    assert new_env.name == "测试环境", "环境名称不正确"
    assert new_env.remark == "测试用途", "环境描述不正确"
    
    # 验证表名
    assert Environment._meta.db_table == 'environment', "环境表名不正确"
    
    print("\n✅ 环境模型测试通过!")
    print(f"- 模型名称: {Environment.__name__}")
    print(f"- 表名: {Environment._meta.db_table}")
    print(f"- 字段: name={new_env.name}, remark={new_env.remark}")
    
    # 测试外键关系
    envir_field = ProjectEnvirData._meta.get_field('envir')
    project_field = ProjectEnvirData._meta.get_field('project')
    
    assert envir_field.related_model == Environment, "环境关联关系不正确"
    assert project_field.related_model == Project, "项目关联关系不正确"
    
    print("\n✅ 关联关系测试通过!")
    print(f"- ProjectEnvirData.envir 关联到: {envir_field.related_model.__name__}")
    print(f"- ProjectEnvirData.project 关联到: {project_field.related_model.__name__}")
    
except Exception as e:
    print(f"\n❌ 测试失败: {str(e)}")
    
print("\n测试完成!")
