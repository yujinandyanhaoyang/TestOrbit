"""
断言规则相关操作
"""
from apiData.models import AssertionRule
from utils.assertion_engine import AssertionEngine
from utils.constant import FAILED
from django.db import IntegrityError
from django.db.models import F
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apiData.models import ApiCaseStep, AssertionRule
from apiData.serializers import AssertionRuleSerializer



# 创建或更新断言
def save_assert(step_id, assert_data):
    # print(f"进入 save_assert 函数，参数如下：\nstep_id: {step_id}\nassert_data: {assert_data}")
    
    # 确保必须提供step_id
    if not step_id:
        return Response(
            data={'msg': '创建断言规则时必须提供step_id！'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 确保assert_data是列表
    if not isinstance(assert_data, list):
        return Response(
            data={'msg': '断言数据必须是一个数组！'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    results = []
    success_count = 0
    error_count = 0
    
    for data in assert_data:
        try:
            rule_id = data.get('id')
            
            if rule_id:
                # 更新现有断言规则
                rule = AssertionRule.objects.filter(id=rule_id).first()
                if not rule:
                    results.append({
                        'id': rule_id,
                        'status': 'error',
                        'msg': f'未找到ID为 {rule_id} 的断言规则！'
                    })
                    error_count += 1
                    continue
                
                serializer = AssertionRuleSerializer(rule, data=data, partial=True)
                operation_type = "更新"
            else:
                # 创建新断言规则
                data['step'] = step_id
                serializer = AssertionRuleSerializer(data=data)
                operation_type = "创建"
                
            if serializer.is_valid():
                rule = serializer.save()
                results.append({
                    'id': rule.id,
                    'status': 'success',
                    'msg': f'断言规则{operation_type}成功！(ID: {rule.id})',
                    'data': serializer.data
                })
                success_count += 1
            else:
                results.append({
                    'id': rule_id,
                    'status': 'error',
                    'msg': f'数据验证失败: {serializer.errors}'
                })
                error_count += 1
                
        except IntegrityError as e:
            results.append({
                'id': data.get('id'),
                'status': 'error',
                'msg': f'{operation_type}断言规则时发生数据库约束错误: {str(e)}'
            })
            error_count += 1
        except Exception as e:
            results.append({
                'id': data.get('id'),
                'status': 'error',
                'msg': f'{operation_type}断言规则时出错: {str(e)}'
            })
            error_count += 1
    
    # 返回整体结果
    return Response(
        data={
            'msg': f'处理完成: {success_count}个成功, {error_count}个失败',
            'results': results
        },
        status=status.HTTP_200_OK if error_count == 0 else status.HTTP_207_MULTI_STATUS
    )



"""
断言执行器模块
负责在API执行过程中进行断言规则的验证
"""
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
    
