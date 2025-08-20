"""
apiData 测试数据可视化脚本
展示 apiData 应用中各个模型的数据，以及模型之间的关系
"""
import os
import sys
from datetime import datetime

# 添加父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TestOrbit.settings')
import django
django.setup()

# 导入模型
from apiData.models import ApiModule, ApiData, ApiCaseModule, ApiCase, ApiCaseStep
from django.db.models import Count


def print_header(title):
    """打印格式化的标题"""
    print("\n" + "="*80)
    print(" "*((80 - len(title))//2) + title)
    print("="*80)


def print_table(data, headers):
    """打印格式化表格"""
    # 计算每列的最大宽度
    col_widths = [len(h) for h in headers]
    for row in data:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # 打印表头
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    print(header_line)
    print("-" * len(header_line))
    
    # 打印数据行
    for row in data:
        line = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
        print(line)


def view_api_modules():
    """查看API模块数据"""
    print_header("API模块数据")
    
    modules = ApiModule.objects.all().annotate(api_count=Count('apidata'))
    
    if not modules.exists():
        print("没有API模块数据。请先运行 generate_test_data.py 创建测试数据。")
        return
    
    data = []
    for module in modules:
        data.append([
            module.id,
            module.name,
            module.project.name,
            module.position,
            module.api_count,
            module.created.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    headers = ["ID", "名称", "所属项目", "排序", "API数量", "创建时间"]
    print_table(data, headers)


def view_api_data():
    """查看API数据"""
    print_header("API数据")
    
    apis = ApiData.objects.all()
    
    if not apis.exists():
        print("没有API数据。请先运行 generate_test_data.py 创建测试数据。")
        return
    
    data = []
    for api in apis:
        data.append([
            api.id,
            api.name,
            api.path,
            api.method,
            api.project.name,
            api.module.name,
            api.status,
            api.creater.username if api.creater else "未知"
        ])
    
    headers = ["ID", "名称", "路径", "方法", "项目", "模块", "状态", "创建者"]
    print_table(data, headers)


def view_api_case_modules():
    """查看API用例模块数据"""
    print_header("API用例模块数据")
    
    modules = ApiCaseModule.objects.all().annotate(case_count=Count('apicase'))
    
    if not modules.exists():
        print("没有API用例模块数据。请先运行 generate_test_data.py 创建测试数据。")
        return
    
    data = []
    for module in modules:
        data.append([
            module.id,
            module.name,
            module.position,
            module.case_count,
            module.created.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    headers = ["ID", "名称", "排序", "用例数量", "创建时间"]
    print_table(data, headers)


def view_api_cases():
    """查看API测试用例数据"""
    print_header("API测试用例数据")
    
    cases = ApiCase.objects.filter(is_deleted=False).annotate(step_count=Count('case_step'))
    
    if not cases.exists():
        print("没有API测试用例数据。请先运行 generate_test_data.py 创建测试数据。")
        return
    
    data = []
    for case in cases:
        data.append([
            case.id,
            case.name,
            case.module.name,
            case.status,
            case.step_count,
            case.position,
            case.creater.username if case.creater else "未知",
            case.latest_run_time.strftime('%Y-%m-%d %H:%M:%S') if case.latest_run_time else "未运行"
        ])
    
    headers = ["ID", "名称", "模块", "状态", "步骤数", "排序", "创建者", "最后运行时间"]
    print_table(data, headers)


def view_api_case_steps():
    """查看API测试用例步骤数据"""
    print_header("API测试用例步骤数据")
    
    steps = ApiCaseStep.objects.all()
    
    if not steps.exists():
        print("没有API测试用例步骤数据。请先运行 generate_test_data.py 创建测试数据。")
        return
    
    data = []
    for step in steps:
        data.append([
            step.id,
            step.step_name,
            step.case.name,
            step.type,
            step.status,
            step.api.name if step.api else "N/A",
            "是" if step.enabled else "否"
        ])
    
    headers = ["ID", "名称", "所属用例", "类型", "状态", "关联接口", "启用"]
    print_table(data, headers)


def view_data_relationships():
    """查看数据关系"""
    print_header("数据关系视图")
    
    # 随机选择一个测试用例及其相关数据来展示关系
    case = ApiCase.objects.filter(is_deleted=False).first()
    
    if not case:
        print("没有API测试用例数据。请先运行 generate_test_data.py 创建测试数据。")
        return
    
    print(f"测试用例: {case.name} (ID: {case.id})")
    print(f"├── 所属模块: {case.module.name} (ID: {case.module.id})")
    print(f"├── 创建者: {case.creater.username if case.creater else '未知'}")
    print(f"└── 步骤列表:")
    
    steps = ApiCaseStep.objects.filter(case=case)
    for i, step in enumerate(steps):
        print(f"    ├── 步骤{i+1}: {step.step_name}")
        if step.api:
            api = step.api
            print(f"    │   ├── 关联接口: {api.name}")
            print(f"    │   ├── 接口路径: {api.method} {api.path}")
            print(f"    │   └── 接口所属模块: {api.module.name}")
    
    if not steps:
        print("    └── (无步骤)")


def main():
    """主函数，运行所有视图"""
    print_header("apiData 测试数据可视化")
    
    view_api_modules()
    view_api_data()
    view_api_case_modules()
    view_api_cases()
    view_api_case_steps()
    view_data_relationships()
    
    print("\n" + "="*80)
    print(" "*30 + "数据查看完成")
    print("="*80)


if __name__ == "__main__":
    main()
