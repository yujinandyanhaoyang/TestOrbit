"""
运行所有单元测试
"""
import os
import sys
import unittest
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TestOrbit.settings')
django.setup()

from django.test.runner import DiscoverRunner

def run_tests():
    # 创建测试运行器
    test_runner = DiscoverRunner(verbosity=2, interactive=True)
    failures = test_runner.run_tests(['test'])
    return failures

if __name__ == '__main__':
    failures = run_tests()
    sys.exit(bool(failures))
