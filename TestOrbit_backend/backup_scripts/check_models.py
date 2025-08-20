"""
简单测试检查
用于检查项目和配置模型是否正确映射
"""
from django.core.management import execute_from_command_line
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TestOrbit.settings')
django.setup()

# 导入模型
from project.models import Project, ProjectParamType
from config.models import Environment, ProjectEnvirData

# 检查表名
print("\n=== 检查模型表映射 ===")
print(f"Project 表名: {Project._meta.db_table}")
print(f"ProjectParamType 表名: {ProjectParamType._meta.db_table}")
print(f"Environment 表名: {Environment._meta.db_table}")
print(f"ProjectEnvirData 表名: {ProjectEnvirData._meta.db_table}")

# 检查字段
print("\n=== 检查关键字段 ===")
print(f"Project.name 是否唯一: {Project._meta.get_field('name').unique}")
print(f"Project.name 最大长度: {Project._meta.get_field('name').max_length}")
print(f"Environment.name 是否唯一: {Environment._meta.get_field('name').unique}")
print(f"Environment.name 最大长度: {Environment._meta.get_field('name').max_length}")

# 检查外键关系
print("\n=== 检查外键关系 ===")
print(f"ProjectEnvirData.envir 关联到: {ProjectEnvirData._meta.get_field('envir').related_model.__name__}")
print(f"ProjectEnvirData.project 关联到: {ProjectEnvirData._meta.get_field('project').related_model.__name__}")

print("\n检查完成！")
