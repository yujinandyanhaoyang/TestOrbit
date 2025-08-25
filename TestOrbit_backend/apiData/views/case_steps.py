"""
apiData/views/case_steps.py - 用例步骤管理视图

处理用例步骤的所有操作，包括：
1. 添加步骤到用例
2. 更新步骤信息
3. 删除步骤
4. 调整步骤顺序
"""

import datetime
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apiData.models import ApiCase, ApiCaseStep, ApiForeachStep
from utils.constant import API, API_CASE, API_FOREACH, USER_API
from apiData.views.function.viewDef import parse_create_foreach_steps

@api_view(['POST'])
def add_steps(request):
    """添加步骤到用例
    
    处理单个或多个步骤的添加操作
    支持API步骤、用例引用步骤和循环步骤
    """
    case_id = request.data.get('case_id')
    steps = request.data.get('steps', [])
    
    if not case_id or not steps:
        return Response({
            'message': '缺少必要参数'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        with transaction.atomic():
            # 获取当前最大步骤顺序
            max_order = ApiCaseStep.objects.filter(case_id=case_id).count()
            
            steps_objs = []
            foreach_steps = []
            api_data_to_create = []
            have_foreach = False
            
            # 处理每个步骤
            for step_index, step in enumerate(steps, start=max_order+1):
                # 步骤基本信息
                step_basic_data = {
                    'case_id': case_id,
                    'step_order': step_index,
                    'step_name': step.get('step_name', ''),
                    'type': step['type'],
                    'enabled': step.get('enabled', True),
                    'controller_data': step.get('controller_data'),
                    'retried_times': step.get('retried_times', 0)
                }
                
                s_type = step['type']
                if s_type == API:
                    # API类型步骤
                    step_params = step.get('params', {})
                    api_data_dict = {
                        'name': step.get('step_name', f'API步骤_{step_index}'),
                        'path': step_params.get('path', ''),
                        'method': step_params.get('method', ''),
                        'env_id': step_params.get('env_id'),
                        'timeout': step_params.get('timeout', 30),
                        'module_id': 'APM00000001',
                        'source': USER_API,
                        'is_step_instance': True,
                        'params': step_params,
                        'creater_id': request.user.id,
                        'updater_id': request.user.id
                    }
                    api_data_to_create.append((step_basic_data, api_data_dict))
                    
                elif s_type == API_CASE:
                    # 用例引用类型步骤
                    step_params = step.get('params', {})
                    step_basic_data['quote_case_id'] = (
                        step_params.get('case_related', [])[-1] 
                        if step_params.get('case_related') else None
                    )
                    steps_objs.append(ApiCaseStep(**step_basic_data))
                    
                elif s_type == API_FOREACH:
                    # 循环步骤
                    have_foreach = True
                    foreach_steps.append({
                        'steps': step.get('params', {}).get('steps', []),
                        'step_order': step_index
                    })
                    steps_objs.append(ApiCaseStep(**step_basic_data))
                    
                else:
                    # 其他类型步骤
                    steps_objs.append(ApiCaseStep(**step_basic_data))
                    
            # 创建API数据并关联
            for step_data, api_data_dict in api_data_to_create:
                # 将API数据直接整合到步骤中
                step_data.update(api_data_dict)
                steps_objs.append(ApiCaseStep(**step_data))
                
            # 批量创建步骤
            created_steps = ApiCaseStep.objects.bulk_create(steps_objs)
            
            # 处理循环步骤
            if have_foreach:
                for_next_id = 1
                case_steps = ApiCaseStep.objects.filter(
                    case_id=case_id, 
                    type=API_FOREACH
                )
                step_mapping = {step.step_order: step for step in case_steps}
                
                save_step_objs = []
                for foreach_step in foreach_steps:
                    parent_step = step_mapping.get(foreach_step['step_order'])
                    if parent_step:
                        for_next_id = parse_create_foreach_steps(
                            save_step_objs,
                            foreach_step['steps'],
                            parent_step,
                            for_next_id
                        )
                ApiForeachStep.objects.bulk_create(save_step_objs)
                
            # 更新用例更新时间
            ApiCase.objects.filter(id=case_id).update(
                updater_id=request.user.id,
                updated=datetime.datetime.now()
            )
            
            return Response({
                'message': '添加步骤成功',
                'step_count': len(created_steps)
            })
            
    except Exception as e:
        print(f'添加步骤失败: {str(e)}')
        return Response({
            'message': f'添加步骤失败: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def update_step(request):
    """更新步骤信息"""
    step_id = request.data.get('step_id')
    if not step_id:
        return Response({
            'message': '缺少step_id参数'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        step = ApiCaseStep.objects.get(id=step_id)
        
        # 更新基本信息
        for field in ['step_name', 'enabled', 'controller_data']:
            if field in request.data:
                setattr(step, field, request.data[field])
                
        # 更新API相关信息
        if step.type == API:
            if 'params' in request.data:
                step.params = request.data['params']
                
        step.save()
        
        # 更新用例更新时间
        ApiCase.objects.filter(id=step.case_id).update(
            updater_id=request.user.id,
            updated=datetime.datetime.now()
        )
        
        return Response({'message': '更新成功'})
        
    except ApiCaseStep.DoesNotExist:
        return Response({
            'message': '步骤不存在'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        return Response({
            'message': f'更新失败: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def delete_step(request):
    """删除步骤"""
    step_id = request.data.get('step_id')
    if not step_id:
        return Response({
            'message': '缺少step_id参数'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        step = ApiCaseStep.objects.get(id=step_id)
        case_id = step.case_id
        
        with transaction.atomic():
            # API步骤数据会随步骤一起删除，不需要额外操作
            if step.type == API:
                pass  # 数据已经整合到ApiCaseStep，删除step时会自动删除数据
                
            # 如果是foreach步骤，删除子步骤
            elif step.type == API_FOREACH:
                ApiForeachStep.objects.filter(step_id=step_id).delete()
                
            # 删除步骤
            step.delete()
            
            # 重新排序剩余步骤
            remaining_steps = ApiCaseStep.objects.filter(
                case_id=case_id,
                step_order__gt=step.step_order
            ).order_by('step_order')
            
            for i, s in enumerate(remaining_steps, start=step.step_order):
                s.step_order = i
                
            ApiCaseStep.objects.bulk_update(
                remaining_steps,
                ['step_order']
            )
            
            # 更新用例更新时间
            ApiCase.objects.filter(id=case_id).update(
                updater_id=request.user.id,
                updated=datetime.datetime.now()
            )
            
        return Response({'message': '删除成功'})
        
    except ApiCaseStep.DoesNotExist:
        return Response({
            'message': '步骤不存在'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        return Response({
            'message': f'删除失败: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def reorder_steps(request):
    """调整步骤顺序"""
    case_id = request.data.get('case_id')
    step_orders = request.data.get('step_orders', [])
    
    if not case_id or not step_orders:
        return Response({
            'message': '缺少必要参数'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        # 验证步骤是否都属于同一用例
        steps = ApiCaseStep.objects.filter(
            case_id=case_id,
            id__in=[so['step_id'] for so in step_orders]
        )
        if len(steps) != len(step_orders):
            return Response({
                'message': '部分步骤不存在或不属于该用例'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # 更新步骤顺序
        step_dict = {s.id: s for s in steps}
        for order_info in step_orders:
            step = step_dict[order_info['step_id']]
            step.step_order = order_info['new_order']
            
        ApiCaseStep.objects.bulk_update(steps, ['step_order'])
        
        # 更新用例更新时间
        ApiCase.objects.filter(id=case_id).update(
            updater_id=request.user.id,
            updated=datetime.datetime.now()
        )
        
        return Response({'message': '更新顺序成功'})
        
    except Exception as e:
        return Response({
            'message': f'更新顺序失败: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
