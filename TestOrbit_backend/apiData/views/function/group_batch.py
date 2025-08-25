"""
批量执行API用例相关功能模块

本模块提供批量执行API测试用例的相关功能，支持并行和串行两种执行方式。
"""

import datetime
from rest_framework import status
from rest_framework.response import Response
from apiData.models import ApiCase
from utils.constant import RUNNING, WAITING
from user.models import UserCfg
import concurrent.futures 

# 功能函数切分保存位置,变更到其他位置
from .group_def import run_api_case_func, parse_api_case_steps


class BatchExecutionException(Exception):
    """批量执行过程中的异常类"""
    def __init__(self, message, status_code=status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def handleGroupbatch(batch_params, user_id):
    """
    批量执行API用例的核心处理函数
    
    Args:
        batch_params: 包含case_ids和parallel参数的字典
        user_id: 当前用户ID
        
    Returns:
        dict: 执行结果数据
        
    Raises:
        BatchExecutionException: 执行过程中发生的异常
    """
    print("已进入batch_run_api_cases函数，准备批量运行选中的用例组")
    case_ids = batch_params.get('case_ids', [])
    parallel = batch_params.get('parallel', 0)  # 1表示并行，0表示串行

    if not case_ids:
        raise BatchExecutionException("请选择至少一个测试用例")

    # 获取所有要执行的用例数据，同时获取环境信息
    cases_to_run = {}
    environment_conflicts = []
    first_env_id = None

    for case_id in case_ids:
        try:
            case = ApiCase.objects.get(id=case_id)
            if case.env is None:
                raise BatchExecutionException(f"用例 '{case.name}' (ID: {case_id}) 没有设置环境，请先为该用例配置环境")
            
            # 检查环境一致性
            if first_env_id is None:
                first_env_id = case.env.id
            elif first_env_id != case.env.id:
                environment_conflicts.append(f"用例 '{case.name}' 使用环境 '{case.env.name}'")
            
            # 修复：传入列表而不是单个整数
            case_data = parse_api_case_steps([case_id])
            # 从字典中提取步骤列表
            step_list = case_data.get(case_id, []) if isinstance(case_data, dict) else []
            cases_to_run[case_id] = {
                'case_data': step_list,  # 直接存储步骤列表，而不是字典
                'env_id': case.env.id,
                'case_name': case.name
            }
        except ApiCase.DoesNotExist:
            print(f"用例ID {case_id} 不存在")
            raise BatchExecutionException(f"用例ID {case_id} 不存在")
        except BatchExecutionException:
            # 直接传递自定义异常
            raise
        except Exception as e:
            print(f"准备用例 {case_id} 时发生错误: {str(e)}")
            raise BatchExecutionException(f"准备用例 {case_id} 时发生错误: {str(e)}")

    # 如果有环境冲突，给出警告但仍然继续执行
    if environment_conflicts:
        print(f"警告：检测到不同环境的用例，可能会影响测试结果: {environment_conflicts}")

    # 设置用户配置，确保步骤失败不会中断执行
    # 使用第一个用例的环境ID作为默认环境
    UserCfg.objects.update_or_create(
        user_id=user_id, 
        defaults={
            'exec_status': RUNNING, 
            'envir_id': first_env_id,
            'failed_stop': False
        }
    )

    results = []
    start_time = datetime.datetime.now()
    execution_mode = 'parallel' if parallel == 1 else 'serial'

    try:
        if parallel == 1:
            print('采用并行模式执行测试用例')
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(case_ids), 5)) as executor:
                # 创建一个任务字典，记录每个future对应的case_id
                future_to_case = {}
                
                # 提交所有任务到线程池
                for case_id, case_info in cases_to_run.items():
                    # 准备每个用例的执行配置
                    cfg_data = {
                        'envir_id': case_info['env_id'],
                        'failed_stop': False
                    }
                    
                    future = executor.submit(
                        run_api_case_func,
                        case_info['case_data'],  # 直接传入步骤列表
                        user_id,
                        cfg_data
                    )
                    future_to_case[future] = {
                        'case_id': case_id,
                        'case_name': case_info['case_name'],
                        'env_id': case_info['env_id']
                    }
                
                # 获取每个任务的结果
                for future in concurrent.futures.as_completed(future_to_case):
                    case_info = future_to_case[future]
                    try:
                        result = future.result()
                        results.append({
                            'case_id': case_info['case_id'],
                            'case_name': case_info['case_name'],
                            'env_id': case_info['env_id'],
                            'status': 'success',
                            'result': result
                        })
                    except Exception as e:
                        results.append({
                            'case_id': case_info['case_id'],
                            'case_name': case_info['case_name'],
                            'env_id': case_info['env_id'],
                            'status': 'failed',
                            'error': str(e)
                        })
        else:
            print('采用串行模式执行测试用例')
            # 串行执行测试用例
            for case_id, case_info in cases_to_run.items():
                try:
                    print(f"开始执行用例ID {case_id} - {case_info['case_name']}")
                    # 准备每个用例的执行配置
                    cfg_data = {
                        'envir_id': case_info['env_id'],
                        'failed_stop': False
                    }
                    
                    result = run_api_case_func(
                        case_info['case_data'],  # 直接传入步骤列表
                        user_id,
                        cfg_data
                    )
                    print(f"串行模式下，用例ID {case_id} - {case_info['case_name']} 执行结果: {result}")
                    results.append({
                        'case_id': case_id,
                        'case_name': case_info['case_name'],
                        'env_id': case_info['env_id'],
                        'status': 'success',
                        'result': result
                    })
                except Exception as e:
                    results.append({
                        'case_id': case_id,
                        'case_name': case_info['case_name'],
                        'env_id': case_info['env_id'],
                        'status': 'failed',
                        'error': str(e)
                    })
        print('所有测试用例执行完成，更新用户状态')
        # 执行完成后，更新用户状态
        UserCfg.objects.filter(user_id=user_id).update(exec_status=WAITING)
        
        # 计算执行时间
        end_time = datetime.datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # 准备返回结果
        success_count = sum(1 for r in results if r['status'] == 'success')
        fail_count = sum(1 for r in results if r['status'] == 'failed')
        print('准备返回结果')
        response_data = {
            'message': f"批量执行完成！共 {len(results)} 个用例，成功 {success_count} 个，失败 {fail_count} 个",
            'execution_time': execution_time,
            'execution_mode': execution_mode,
            'data': results
        }
        
        # 如果有环境冲突，在响应中添加警告信息
        if environment_conflicts:
            response_data['warning'] = f"检测到不同环境的用例: {environment_conflicts}"
        
        return response_data
        
    except Exception as e:
        UserCfg.objects.filter(user_id=user_id).update(exec_status=WAITING)
        if isinstance(e, BatchExecutionException):
            raise
        else:
            raise BatchExecutionException(f"批量执行异常：{str(e)}")
