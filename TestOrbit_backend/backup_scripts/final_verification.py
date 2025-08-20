"""
最终验证脚本
"""
import os
import sys

# 添加父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TestOrbit.settings')
import django
django.setup()

# 导入模型
from apiData.models import ApiModule, ApiData, ApiCaseModule, ApiCase, ApiCaseStep

print("=== 数据验证 ===")
print(f"API模块数量: {ApiModule.objects.count()}")
print(f"API数据数量: {ApiData.objects.count()}")
print(f"用例模块数量: {ApiCaseModule.objects.count()}")
print(f"测试用例数量: {ApiCase.objects.count()}")
print(f"用例步骤数量: {ApiCaseStep.objects.count()}")

if all([
    ApiModule.objects.count() > 0,
    ApiData.objects.count() > 0, 
    ApiCaseModule.objects.count() > 0,
    ApiCase.objects.count() > 0,
    ApiCaseStep.objects.count() > 0
]):
    print("\n✅ 所有数据都已成功插入！测试数据生成完成！")
else:
    print("\n❌ 某些数据可能插入失败。")

print("=== 验证完成 ===")
