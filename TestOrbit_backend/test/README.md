# TestOrbit 测试框架

本目录包含 TestOrbit 项目的测试框架和测试用例。通过这些测试，可以确保项目的各个组件正常工作。

## 目录结构

```
test/
├── __init__.py          # 测试包初始化文件
├── apiData/             # API数据相关测试
├── config/              # 配置相关测试
├── integration/         # 跨应用集成测试
├── project/             # 项目相关测试
├── TestOrbit/           # 核心应用测试
├── utils/               # 工具类测试
├── generate_test_data.py # 测试数据生成器
└── run_tests.py         # 测试运行脚本
```

## 运行测试

可以使用项目根目录下的 `run_tests.py` 脚本运行测试：

```bash
# 显示帮助信息
python run_tests.py --help

# 运行所有测试
python run_tests.py --all

# 运行特定应用的测试
python run_tests.py --api
python run_tests.py --project
python run_tests.py --config
python run_tests.py --utils
python run_tests.py --integration
python run_tests.py --urls

# 生成测试数据
python run_tests.py --generate-data
```

## 测试数据生成

`generate_test_data.py` 提供了一个 `TestDataGenerator` 类，可以用来生成各种测试数据。这个类可以独立使用，也可以在测试中使用：

```python
from test.generate_test_data import TestDataGenerator

# 创建生成器实例
generator = TestDataGenerator()

# 生成所有测试数据
generator.generate_all_test_data()

# 或者只生成特定类型的数据
users = generator.create_users(3)
projects = generator.create_projects(2)
```

## 添加新测试

要添加新的测试，只需在相应的应用目录下创建一个以 `test_` 开头的文件，并定义继承自 `unittest.TestCase` 或 `django.test.TestCase` 的测试类：

```python
from django.test import TestCase

class MyNewTest(TestCase):
    def setUp(self):
        # 测试准备工作
        pass
        
    def test_something(self):
        # 测试逻辑
        self.assertEqual(1 + 1, 2)
```

## 测试覆盖率

要查看测试覆盖率，可以安装和使用 `coverage` 工具：

```bash
pip install coverage
coverage run run_tests.py --all
coverage report
coverage html  # 生成HTML报告
```
