"""
断言执行器模块
负责在API执行过程中进行断言规则的验证
"""
import copy

from apiData.models import AssertionRule
from utils.assertion_engine import AssertionEngine
from utils.constant import FAILED

def execute_assertions(step_id, response, status_code=None, headers=None):
    """
    执行API断言规则
    
    Args:
        step_id (int): API步骤ID
        response: 响应体数据（主要的断言目标）
        status_code (int, optional): HTTP状态码
        headers (dict, optional): 响应头信息
        
    Returns:
        dict: 断言执行结果
        {
            'passed': bool,  # 所有断言是否通过
            'results': list,  # 详细的断言结果列表
            'summary': str   # 结果摘要信息
        }
    """
    # print("\n🔍 执行断言规则...")
    # print(f"当前步骤ID: {step_id}")
    # print(f'response:{response}')
    # 如果step_id没有关联断言，则跳过
    # 查找当前step_id的所有断言规则
    assertion_rules = AssertionRule.objects.filter(step_id=step_id, enabled=True)
    if not assertion_rules:
        # print("ℹ️ 没有找到断言规则，跳过断言验证")
        return {
            'passed': True,
            'results': [],
            'summary': '无断言规则'
        }

    # 查询该步骤的所有启用的断言规则
    assertion_rules = AssertionRule.objects.filter(
        step_id=step_id, 
        enabled=True
    ).order_by('id')  # 使用id排序
    
    if not assertion_rules:
        print("ℹ️ 没有找到断言规则，跳过断言验证")
        return {
            'passed': True,
            'results': [],
            'summary': '无断言规则'
        }
        
    print(f"✅ 找到 {assertion_rules.count()} 条断言规则")
    
    # 准备断言数据，主要针对响应体
    assertion_data = {
        'status_code': status_code,
        'headers': headers or {},
        'body': response  # 主要的断言目标
    }
    
    # 执行断言规则
    assertion_results = AssertionEngine.assert_response(assertion_data, assertion_rules)
    
    # print(f"📋 断言结果: {assertion_results}")
    
    # 分析断言结果
    # 注意：断言结果中使用的字段是 'success' 而不是 'passed'
    failed_results = [result for result in assertion_results if not result.get('success', False)]
    passed_results = [result for result in assertion_results if result.get('success', False)]
    
    if failed_results:
        # print(f"❌ {len(failed_results)} 个断言失败, {len(passed_results)} 个通过")
        summary = f"断言失败: {len(failed_results)}/{len(assertion_results)} 失败"
    else:
        # print(f"✅ 所有 {len(assertion_results)} 个断言通过")
        summary = f"所有断言通过 ({len(assertion_results)}个)"
        
    # print(f"🏁 断言执行完成")
    
    return {
        'passed': len(failed_results) == 0,
        'results': assertion_results,
        'summary': summary
    }
    
