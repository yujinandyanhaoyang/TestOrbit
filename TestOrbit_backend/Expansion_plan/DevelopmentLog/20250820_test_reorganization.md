# TestOrbit 项目重构与TDD实践记录

## 测试驱动开发(TDD)与技术债务解决方案

本项目使用测试驱动开发(TDD)方法重构了原有代码，解决了以下技术债务：

1. 项目结构与命名不一致问题（conf应用 -> config应用）
2. 数据模型表名映射问题（ConfEnvir -> Project）
3. URL路由冲突与重定向问题
4. 测试覆盖率不足问题

## 测试框架结构

项目的测试已经整合到统一的测试目录 `test/` 中：

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
└── README.md            # 测试文档
```

## 运行测试

使用项目根目录下的 `run_tests.py` 脚本运行测试：

```bash
# 显示帮助信息
python run_tests.py --help

# 运行所有测试
python run_tests.py --all

# 运行特定测试
python run_tests.py --api
python run_tests.py --project
```

## 测试数据生成

使用 `--generate-data` 选项可以生成测试数据：

```bash
python run_tests.py --generate-data
```

## 开发记录

项目中移除了以下临时文件，以保持代码库的整洁：
- 临时测试脚本（如test_project.py, test_environment.py）
- 数据插入脚本（如batch_insert_test_data.py）
- 验证和检查脚本（如check_db.py, final_verification.py）

这些文件的备份可以在 `backup_scripts/` 目录中找到。
