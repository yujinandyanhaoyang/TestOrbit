"""
测试项目配置
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TestOrbit.settings')
django.setup()

# 导入需要测试的模型
from project.models import Project

# 简单测试: 创建项目实例并验证
try:
    # 尝试创建一个新项目
    new_project = Project(name="测试项目", position=1)
    
    # 验证属性
    assert new_project.name == "测试项目", "项目名称不正确"
    assert new_project.position == 1, "项目位置不正确"
    
    # 验证表名
    assert Project._meta.db_table == 'project', "项目表名不正确"
    
    print("\n✅ 项目模型测试通过!")
    print(f"- 模型名称: {Project.__name__}")
    print(f"- 表名: {Project._meta.db_table}")
    print(f"- 字段: name={new_project.name}, position={new_project.position}")
    
except Exception as e:
    print(f"\n❌ 测试失败: {str(e)}")
    
print("\n测试完成!")
