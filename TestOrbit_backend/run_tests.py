#!/usr/bin/env python
"""
测试套件入口文件
用于运行所有测试或特定测试套件
"""
import os
import sys
import unittest
from django.conf import settings

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TestOrbit.settings')
import django
django.setup()

from django.test.runner import DiscoverRunner

def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*80)
    print(" "*30 + "运行所有测试")
    print("="*80)
    
    # 创建测试运行器
    test_runner = DiscoverRunner(verbosity=2, interactive=True)
    failures = test_runner.run_tests(['test'])
    return failures

def run_specific_tests(test_label):
    """运行特定的测试"""
    print(f"\n运行测试: {test_label}")
    test_runner = DiscoverRunner(verbosity=2, interactive=True)
    failures = test_runner.run_tests([f'test.{test_label}'])
    return failures

def print_usage():
    """打印使用说明"""
    print("\nTestOrbit测试运行工具")
    print("\n用法: python run_tests.py [选项]")
    print("\n选项:")
    print("  --all                 运行所有测试")
    print("  --api                 运行API数据相关测试")
    print("  --project             运行项目相关测试")
    print("  --config              运行配置相关测试")
    print("  --utils               运行工具类测试")
    print("  --integration         运行集成测试")
    print("  --urls                运行URL路由测试")
    print("  --generate-data       生成测试数据")
    print("  --help                显示此帮助信息")
    print("\n示例: python run_tests.py --api")

if __name__ == '__main__':
    # 如果没有参数或者有--help参数，显示使用说明
    if len(sys.argv) == 1 or '--help' in sys.argv:
        print_usage()
        sys.exit(0)
    
    # 根据参数运行不同的测试
    if '--all' in sys.argv:
        failures = run_all_tests()
    elif '--api' in sys.argv:
        failures = run_specific_tests('apiData')
    elif '--project' in sys.argv:
        failures = run_specific_tests('project')
    elif '--config' in sys.argv:
        failures = run_specific_tests('config')
    elif '--utils' in sys.argv:
        failures = run_specific_tests('utils')
    elif '--integration' in sys.argv:
        failures = run_specific_tests('integration')
    elif '--urls' in sys.argv:
        failures = run_specific_tests('TestOrbit')
    elif '--generate-data' in sys.argv:
        # 导入测试数据生成器并生成数据
        from test.generate_test_data import TestDataGenerator
        generator = TestDataGenerator()
        generator.generate_all_test_data()
        failures = 0
    else:
        print("未知选项，使用 --help 查看帮助")
        sys.exit(1)
    
    # 退出码为测试失败的数量
    sys.exit(bool(failures))
