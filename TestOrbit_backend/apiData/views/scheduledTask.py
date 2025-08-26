
import datetime

from django.db import IntegrityError, transaction
from django.db.models import  Max
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apiData.models import ApiCaseModule, ApiCase, ApiModule, ApiCaseStep, ApiForeachStep
from apiData.serializers import ApiCaseListSerializer, ApiCaseSerializer, ApiCaseDetailSerializer
from utils.comDef import get_module_related, get_case_sort_list
from utils.constant import DEFAULT_MODULE_NAME, USER_API, API, FAILED, API_CASE, API_FOREACH, SUCCESS, RUNNING, WAITING, INTERRUPT
from utils.views import View
from user.models import UserCfg
from .caseStep import parse_api_case_steps,run_api_case_func,set_user_temp_params
from .function.viewDef import parse_create_foreach_steps


from .function.scheduled_tasks_def import create_scheduled_task, get_scheduled_tasks, cancel_scheduled_task, update_scheduled_task

@api_view(['POST'])
def schedule_api_cases(request):
    """
    创建或更新定时执行API用例任务
    
    创建任务请求体格式：
    {
        "case_ids": [22, 20],                // api_case 的id列表
        "parallel": 1,                       // 运行模式：0串行，1并行
        "owner_ids": [1, 2],                // 负责人user_id列表
        "startTime": "2025-08-26T11:00:00"  // 预定运行时间（ISO 8601格式）
    }
    
    更新任务请求体格式（完全更新，必须包含所有字段）：
    {
        "task_id": 1,                        // 任务ID（必须，用于标识更新操作）
        "case_ids": [25, 30],                // 新的api_case的id列表（必须）
        "parallel": 0,                       // 新的运行模式：0串行，1并行（必须）
        "owner_ids": [1, 3],                // 新的负责人user_id列表（必须）
        "startTime": "2025-08-26T16:30:00"  // 新的预定运行时间（必须）
    }
    
    注意：更新操作必须提供所有字段，缺少任何字段都会返回"缺少必要参数"错误
    """
    try:
        # 检查是否包含task_id来判断是创建还是更新
        task_id = request.data.get('task_id')
        
        if task_id:
            # 更新任务
            result = update_scheduled_task(task_id, request.user.id, request.data)
            return Response({
                'message': '定时任务更新成功！',
                'data': result
            })
        else:
            # 创建任务
            result = create_scheduled_task(request.data, request.user.id)
            return Response({
                'message': '定时任务创建成功！',
                'data': result
            })
            
    except ValueError as e:
        return Response({
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        operation = "更新" if request.data.get('task_id') else "创建"
        return Response({
            'message': f'{operation}定时任务失败：{str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_scheduled_tasks_list(request):
    """
    获取定时任务列表
    
    查询参数：
    - status: 任务状态过滤（pending, running, completed, failed, cancelled）
    """
    try:
        # 检查参数中是否有状态过滤，没有则返回所有定时任务
        status_filter = request.query_params.get('status')
        tasks = get_scheduled_tasks(request.user.id, status_filter)
        return Response({
            'message': '获取任务列表成功',
            'data': tasks,
            'total': len(tasks)
        })
    except Exception as e:
        return Response({
            'message': f'获取任务列表失败：{str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def cancel_scheduled_task_api(request):
    """
    取消定时任务
    
    请求体格式：
    {
        "task_id": 1  // 任务ID
    }
    """
    try:
        task_id = request.data.get('task_id')
        if not task_id:
            return Response({
                'message': '缺少任务ID'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = cancel_scheduled_task(task_id, request.user.id)
        return Response(result)
    except ValueError as e:
        return Response({
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'message': f'取消任务失败：{str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
