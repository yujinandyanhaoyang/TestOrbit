"""
定时任务相关功能模块

本模块提供API用例定时执行的相关功能，包括：
1. 定时任务的创建和管理
2. 任务调度和执行
3. 任务状态监控和结果处理
"""

import datetime
import threading
import time
from typing import List, Dict, Any
from django.db import transaction

from apiData.models import ScheduledTask, ApiCase
from user.models import ExpendUser
from .group_batch import handleGroupbatch, BatchExecutionException


class TaskScheduler:
    """
    定时任务调度器
    负责管理和执行定时任务
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """单例模式确保只有一个调度器实例"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._running = False
        self._scheduler_thread = None
    
    def start(self):
        """启动任务调度器"""
        if not self._running:
            self._running = True
            self._scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self._scheduler_thread.start()
            print("定时任务调度器已启动")
    
    def stop(self):
        """停止任务调度器"""
        self._running = False
        if self._scheduler_thread:
            self._scheduler_thread.join()
        print("定时任务调度器已停止")
    
    def _run_scheduler(self):
        """调度器主循环"""
        while self._running:
            try:
                # 检查待执行的任务
                current_time = datetime.datetime.now()
                # print(f"🕐 [{current_time.strftime('%Y-%m-%d %H:%M:%S')}] 定时任务调度器正在检查待执行任务...")
                
                pending_tasks = ScheduledTask.objects.filter(
                    status='pending',
                    scheduled_time__lte=current_time
                )
                
                # print(f"📊 发现 {pending_tasks.count()} 个待执行任务")
                
                for task in pending_tasks:
                    print(f"⏰ 准备执行任务 {task.id}: {task.task_name}")
                    print(f"   预定时间: {task.scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"   当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"   时间差: {(current_time - task.scheduled_time).total_seconds():.1f}秒")
                    self._execute_task(task)
                
                # if pending_tasks.count() == 0:
                #     print("✅ 当前没有待执行的任务")
                
                # 每1分钟检查一次（60秒） - 为了测试方便
                # print(f"💤 调度器休眠1分钟，下次检查时间: {(current_time + datetime.timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(60)  # 1分钟 = 60秒
            except Exception as e:
                print(f"❌ 调度器错误: {str(e)}")
                time.sleep(60)
    
    def _execute_task(self, task: ScheduledTask):
        """执行单个定时任务"""
        try:
            # 更新任务状态为执行中
            task.status = 'running'
            task.actual_start_time = datetime.datetime.now()
            task.execution_count += 1
            task.save()
            
            print(f"🚀 开始执行定时任务: {task.task_name} (ID: {task.id})")
            print(f"   预定时间: {task.scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   实际开始: {task.actual_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 准备批量执行参数
            batch_params = {
                'case_ids': task.case_ids,
                'parallel': task.parallel
            }
            
            # 使用第一个负责人的ID作为执行用户（实际项目中可能需要更复杂的逻辑）
            user_id = task.owner_ids[0] if task.owner_ids else 1
            
            # 执行批量任务
            result_data = handleGroupbatch(batch_params, user_id)
            
            # 更新任务完成状态
            task.status = 'completed'
            task.actual_end_time = datetime.datetime.now()
            task.execution_result = result_data
            task.save()
            
            execution_duration = (task.actual_end_time - task.actual_start_time).total_seconds()
            print(f"✅ 定时任务执行完成: {task.task_name}")
            print(f"   执行耗时: {execution_duration:.2f}秒")
            
        except BatchExecutionException as e:
            # 处理批量执行异常
            task.status = 'failed'
            task.actual_end_time = datetime.datetime.now()
            task.error_message = e.message
            task.save()
            print(f"❌ 定时任务执行失败: {task.task_name} - {e.message}")
            
        except Exception as e:
            # 处理其他异常
            task.status = 'failed'
            task.actual_end_time = datetime.datetime.now()
            task.error_message = str(e)
            task.save()
            print(f"💥 定时任务执行异常: {task.task_name} - {str(e)}")


def create_scheduled_task(request_data: Dict[str, Any], creator_id: int) -> Dict[str, Any]:
    """
    创建定时任务
    
    Args:
        request_data: 请求数据
        creator_id: 创建者ID
        
    Returns:
        Dict: 创建结果
        
    Raises:
        ValueError: 参数验证失败
    """
    
    # 验证必要参数
    required_fields = ['case_ids', 'parallel', 'owner_ids', 'startTime']
    for field in required_fields:
        if field not in request_data:
            raise ValueError(f"缺少必要参数: {field}")
    
    case_ids = request_data['case_ids']
    parallel = request_data['parallel']
    owner_ids = request_data['owner_ids']
    start_time_str = request_data['startTime']
    
    # 验证参数类型和值
    if not isinstance(case_ids, list) or not case_ids:
        raise ValueError("case_ids必须是非空列表")
    
    if parallel not in [0, 1]:
        raise ValueError("parallel必须是0（串行）或1（并行）")
    
    if not isinstance(owner_ids, list) or not owner_ids:
        raise ValueError("owner_ids必须是非空列表")
    
    # 解析时间字符串，使用ISO 8601格式：2025-08-26T11:00:00
    try:
        scheduled_time = datetime.datetime.fromisoformat(start_time_str)
        
        # 由于项目设置USE_TZ=False，使用naive datetime
        if scheduled_time.tzinfo is not None:
            # 如果有时区信息，转换为本地时间并移除时区信息
            scheduled_time = scheduled_time.replace(tzinfo=None)
            
    except ValueError:
        raise ValueError("startTime格式错误，请使用ISO 8601格式：'YYYY-MM-DDTHH:MM:SS'，例如：'2025-08-26T11:00:00'")
    
    # 检查时间是否在未来
    current_time = datetime.datetime.now()
    if scheduled_time <= current_time:
        raise ValueError("预定时间必须是未来时间")
    
    # 验证测试用例是否存在
    existing_cases = ApiCase.objects.filter(id__in=case_ids)
    if len(existing_cases) != len(case_ids):
        missing_ids = set(case_ids) - set(existing_cases.values_list('id', flat=True))
        raise ValueError(f"以下测试用例不存在: {list(missing_ids)}")
    
    # 验证负责人是否存在
    existing_users = ExpendUser.objects.filter(id__in=owner_ids)
    if len(existing_users) != len(owner_ids):
        missing_ids = set(owner_ids) - set(existing_users.values_list('id', flat=True))
        raise ValueError(f"以下用户不存在: {list(missing_ids)}")
    
    # 生成任务名称
    case_names = existing_cases.values_list('name', flat=True)
    task_name = f"定时测试任务 - {', '.join(case_names[:3])}{'等' if len(case_names) > 3 else ''}"
    
    # 创建定时任务
    with transaction.atomic():
        task = ScheduledTask.objects.create(
            task_name=task_name,
            case_ids=case_ids,
            parallel=parallel,
            owner_ids=owner_ids,
            scheduled_time=scheduled_time,
            creater_id=creator_id
        )
    
    return {
        'task_id': task.id,
        'task_name': task.task_name,
        'scheduled_time': task.scheduled_time.strftime('%Y-%m-%d %H:%M:%S'),
        'case_count': len(case_ids),
        'execution_mode': '并行' if parallel == 1 else '串行',
        'owners': list(existing_users.values_list('username', flat=True))
    }


def get_scheduled_tasks(user_id: int, status_filter: str = None) -> List[Dict[str, Any]]:
    """
    获取定时任务列表
    
    Args:
        user_id: 用户ID
        status_filter: 状态过滤器
        
    Returns:
        List: 任务列表
    """
    
    # 基础查询：用户相关的任务
    queryset = ScheduledTask.objects.filter(
        owner_ids__contains=[user_id]
    ).select_related('creater')
    # print(f'当前用户ID: {user_id}, 状态过滤: {status_filter}')
    # 状态过滤
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    tasks = []
    for task in queryset:
        # 获取关联的测试用例信息
        cases = ApiCase.objects.filter(id__in=task.case_ids)
        case_info = [{'id': case.id, 'name': case.name} for case in cases]
        
        # 获取负责人信息
        owners = ExpendUser.objects.filter(id__in=task.owner_ids)
        owner_info = [{'id': user.id, 'username': user.username} for user in owners]
        
        task_data = {
            'id': task.id,
            'task_name': task.task_name,
            'cases': case_info,
            'execution_mode': '并行' if task.parallel == 1 else '串行',
            'owners': owner_info,
            'scheduled_time': task.scheduled_time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': task.status,
            'status_display': dict(ScheduledTask.TASK_STATUS_CHOICES)[task.status],
            'execution_count': task.execution_count,
            'created': task.created.strftime('%Y-%m-%d %H:%M:%S'),
            'creater': task.creater.username if task.creater else '未知'
        }
        
        # 添加执行时间信息
        if task.actual_start_time:
            task_data['actual_start_time'] = task.actual_start_time.strftime('%Y-%m-%d %H:%M:%S')
        if task.actual_end_time:
            task_data['actual_end_time'] = task.actual_end_time.strftime('%Y-%m-%d %H:%M:%S')
        if task.execution_duration:
            task_data['execution_duration'] = f"{task.execution_duration:.2f}秒"
        
        # 添加执行结果
        if task.execution_result:
            task_data['execution_result'] = task.execution_result
        
        # 添加错误信息
        if task.error_message:
            task_data['error_message'] = task.error_message
        
        tasks.append(task_data)
    # print(f"返回任务数量: {len(tasks)}")
    return tasks


def cancel_scheduled_task(task_id: int, user_id: int) -> Dict[str, Any]:
    """
    取消定时任务
    
    Args:
        task_id: 任务ID
        user_id: 用户ID
        
    Returns:
        Dict: 操作结果
    """
    
    try:
        task = ScheduledTask.objects.get(
            id=task_id,
            owner_ids__contains=[user_id]
        )
        task_name = task.task_name
        # 只能取消pending状态的任务
        if task.status in ['pending']:
            task.delete()
            return {
            'success': True,
            'message': f"任务 '{task_name}' 已取消"
        }
        else:
            raise ValueError(f"任务状态为 {task.get_status_display()}，无法取消")
    except ScheduledTask.DoesNotExist:
        raise ValueError("任务不存在或无权限操作")


def update_scheduled_task(task_id: int, user_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    更新定时任务（完全更新，需要提供所有字段）
    
    Args:
        task_id: 任务ID
        user_id: 用户ID
        update_data: 更新数据
        
    Returns:
        Dict: 更新结果
        
    Raises:
        ValueError: 参数验证失败或状态不允许更新
    """
    
    # 验证必要参数
    required_fields = ['case_ids', 'parallel', 'owner_ids', 'startTime']
    missing_fields = []
    
    for field in required_fields:
        if field not in update_data:
            missing_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"缺少必要参数: {', '.join(missing_fields)}")
    
    try:
        # 获取任务并验证权限
        task = ScheduledTask.objects.get(
            id=task_id,
            owner_ids__contains=[user_id]
        )
        
        # 只能更新pending状态的任务
        if task.status != 'pending':
            raise ValueError(f"任务状态为 {task.get_status_display()}，只能修改待执行状态的任务")
        
        # 验证和更新各个字段
        case_ids = update_data['case_ids']
        parallel = update_data['parallel']
        owner_ids = update_data['owner_ids']
        start_time_str = update_data['startTime']
        
        # 验证测试用例ID列表
        if not isinstance(case_ids, list) or not case_ids:
            raise ValueError("case_ids必须是非空列表")
        
        # 验证用例是否存在
        existing_cases = ApiCase.objects.filter(id__in=case_ids)
        if len(existing_cases) != len(case_ids):
            missing_ids = set(case_ids) - set(existing_cases.values_list('id', flat=True))
            raise ValueError(f"以下测试用例不存在: {list(missing_ids)}")
        
        # 验证执行模式
        if parallel not in [0, 1]:
            raise ValueError("parallel必须是0（串行）或1（并行）")
        
        # 验证负责人列表
        if not isinstance(owner_ids, list) or not owner_ids:
            raise ValueError("owner_ids必须是非空列表")
        
        # 验证用户是否存在
        existing_users = ExpendUser.objects.filter(id__in=owner_ids, is_active=True)
        if len(existing_users) != len(owner_ids):
            missing_ids = set(owner_ids) - set(existing_users.values_list('id', flat=True))
            raise ValueError(f"以下用户不存在或已被禁用: {list(missing_ids)}")
        
        # 验证预定时间
        try:
            scheduled_time = datetime.datetime.fromisoformat(start_time_str)
            
            # 移除时区信息（如果有）
            if scheduled_time.tzinfo is not None:
                scheduled_time = scheduled_time.replace(tzinfo=None)
                
        except ValueError:
            raise ValueError("startTime格式错误，请使用ISO 8601格式：'YYYY-MM-DDTHH:MM:SS'")
        
        # 检查时间是否在未来
        current_time = datetime.datetime.now()
        if scheduled_time <= current_time:
            raise ValueError("预定时间必须是未来时间")
        
        # 执行更新
        task.case_ids = case_ids
        task.parallel = parallel
        task.execution_mode = 'parallel' if parallel == 1 else 'serial'
        task.owner_ids = owner_ids
        task.scheduled_time = scheduled_time
        task.task_name = f"API用例定时任务_{scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 保存更新
        task.save()
        
        # 获取关联信息用于返回
        cases = ApiCase.objects.filter(id__in=task.case_ids)
        case_info = [{'id': case.id, 'name': case.name} for case in cases]
        
        owners = ExpendUser.objects.filter(id__in=task.owner_ids)
        owner_info = [{'id': user.id, 'username': user.username} for user in owners]
        
        return {
            'task_id': task.id,
            'task_name': task.task_name,
            'scheduled_time': task.scheduled_time.strftime('%Y-%m-%d %H:%M:%S'),
            'cases': case_info,
            'execution_mode': '并行' if task.parallel == 1 else '串行',
            'owners': owner_info,
            'status': task.status,
            'case_count': len(case_ids)
        }
        
    except ScheduledTask.DoesNotExist:
        raise ValueError("任务不存在或无权限操作")
