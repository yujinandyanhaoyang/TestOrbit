import copy
import datetime
import json
import os
import time
from urllib.parse import urlencode

import requests
from django.db.models import Max, F
from django.db.models.functions import JSONObject
from openpyxl import load_workbook
from requests import ReadTimeout
from rest_framework.response import Response

from apiData.models import ApiCaseStep, ApiCase, ApiForeachStep
from utils.comDef import get_proj_envir_db_data, db_connect, execute_sql_func, \
    close_db_con, json_dumps, JSONEncoder, MyThread, json_loads, format_parm_type_v
from utils.constant import USER_API, VAR_PARAM, HEADER_PARAM, HOST_PARAM, RUNNING, SUCCESS, FAILED, DISABLED, \
    INTERRUPT, SKIP, API_CASE, API_FOREACH, TABLE_MODE, STRING, DIY_CFG, JSON_MODE, PY_TO_CONF_TYPE, CODE_MODE, \
    OBJECT, FAILED_STOP, WAITING, PRO_CFG, FORM_MODE, EQUAL, API_VAR, NOT_EQUAL, \
    CONTAIN, NOT_CONTAIN, TEXT_MODE, API, FORM_FILE_TYPE, FORM_TEXT_TYPE, API_SQL, RES_BODY
from utils.diyException import DiyBaseException, NotFoundFileError
from utils.paramsDef import parse_param_value, run_params_code, parse_temp_params, get_parm_v_by_temp
from config.models import Environment
from user.models import UserCfg, UserTempParams

# 功能函数切分保存位置,变更到其他位置
from .steps_def import go_step
from .monitor_def import monitor_interrupt
# 避免循环引用，在需要时导入 ApiCasesActuator


"""
复制用例方法
"""
def copy_cases_func(request, case_model, step_model, foreach_step_model=None):
    req_data = request.data
    original_case = case_model.objects.get(id=req_data['case_id'])
    
    # 复制 ApiCase，创建新的用例
    new_case = case_model(
        name=original_case.name + '-COPY',
        module=original_case.module,
        status=WAITING,
        remark=original_case.remark,
        env=original_case.env,  # 复制环境设置
        position=original_case.position,
        creater_id=request.user.id,
        updater_id=request.user.id
    )
    new_case.save()
    
    # 获取原用例的所有步骤
    original_steps = step_model.objects.filter(case=original_case).order_by('step_order')
    
    step_objs = []
    foreach_steps_obj = []
    step_id_mapping = {}  # 用于记录原步骤ID到新步骤ID的映射
    
    for original_step in original_steps:
        # 创建新的步骤对象
        new_step = step_model(
            type=original_step.type,
            enabled=original_step.enabled,
            step_name=original_step.step_name,
            step_order=original_step.step_order,
            status=WAITING,  # 重置状态为等待
            retried_times=None,  # 重置重试次数
            controller_data=original_step.controller_data,
            params=original_step.params,
            results=None,  # 清空执行结果
            timeout=original_step.timeout,
            source=original_step.source,
            case=new_case,  # 关联到新的用例
            env=original_step.env,  # 复制环境设置
            quote_case=original_step.quote_case  # 保持引用的用例不变
        )
        new_step.save()
        
        # 记录步骤ID映射关系
        step_id_mapping[original_step.id] = new_step.id
        
        # 如果是循环步骤，需要复制相关的 ApiForeachStep
        if original_step.type == API_FOREACH:
            original_foreach_steps = ApiForeachStep.objects.filter(step=original_step)
            for original_foreach_step in original_foreach_steps:
                new_foreach_step = ApiForeachStep(
                    step_order=original_foreach_step.step_order,
                    step_name=original_foreach_step.step_name,
                    type=original_foreach_step.type,
                    status=WAITING,
                    case=new_case,
                    enabled=original_foreach_step.enabled,
                    controller_data=original_foreach_step.controller_data,
                    quote_case=original_foreach_step.quote_case,
                    retried_times=None,
                    step=new_step,  # 关联到新的步骤
                    parent=original_foreach_step.parent  # 这里可能需要后续处理映射关系
                )
                foreach_steps_obj.append(new_foreach_step)
    
    # 批量创建循环步骤
    if foreach_steps_obj:
        ApiForeachStep.objects.bulk_create(foreach_steps_obj)
    
    return Response(data={'msg': "复制成功！", 'new_case_id': new_case.id})


"""
转化API计划步骤
is_step:false代表非步骤中的用例，即外层计划列表中选中执行的用例
"""
def parse_api_case_steps(case_ids=None, is_step=False):
    step_data = []
    if case_ids:
        # 处理单个ID或ID列表的情况
        if isinstance(case_ids, (int, str)):
            case_ids = [case_ids]  # 转换为列表
        elif not hasattr(case_ids, '__iter__'):
            # 如果不是可迭代对象，转换为列表
            case_ids = [case_ids]
        
        # 使用正确的外键字段名
        step_data = list(ApiCaseStep.objects.filter(case__in=case_ids).select_related(
            'case', 'case__module').values(
            'case_id', 'step_order', 'step_name', 'type', 'status', 'results', 'id',
            'controller_data', 'enabled','params').order_by('case_id', 'step_order'))
        
        
        if not is_step:  # 如果非测试计划步骤而是执行测试用例，需要转为{case_id:[step,step],case_id2:[step,step]}的形式
            case_data = {case_id: [] for case_id in case_ids}  # {case1:steps,case2:steps}
            for step in step_data:
                case_data[step['case_id']].append(step)
            return case_data
    return step_data


"""
执行完成后，写入结果
"""
def save_results(case_data):
    # 只更新用例的状态和报告数据
    if case_data:
        ApiCase.objects.bulk_update(case_data, fields=('status', 'report_data', 'latest_run_time'))
        print(f'成功更新 {len(case_data)} 个用例的状态和报告数据')



"""
执行步骤合集
"""
def run_step_groups(actuator_obj, step_data, prefix_label='', cascader_level=0, i=0):
    # 默认测试是通过的
    run_status = SUCCESS
    print('开始使用run_step_groups函数执行步骤合集')
    # print(f'步骤合集内容: {step_data}')
    for step in step_data:
        # 往step中添加step_id，方便后续引用
        step['step_id'] = step.get('id')
        step_id = step.get('id')
        s_type = step['type']
        # print(f'开始执行步骤: {step["step_name"]}，类型: {s_type}')
        if step.get('enabled'):

            params = {'actuator_obj': actuator_obj, 'step_id': step_id, 'prefix_label': prefix_label,
                      'i': i}  # 将step传递给go_step
            if s_type in (API_CASE, API_FOREACH):
                params['cascader_level'] = cascader_level + 1
            # print(f'params:{params}\t')
            res = go_step(**params)
            # print(f'{step["step_name"]}步骤执行结果: {res}')

            # 更新步骤状态和结果
            step['status'] = res.get('status', WAITING)  # 设置默认值为WAITING
            if 'data' in res:
                step['data'] = res['data']
            if 'results' in res:
                step['results'] = res['results']
                
            print(f"步骤 {step['step_name']} 执行完成，状态: {step['status']}")
        else:
            step['status'] = DISABLED
            print(f"步骤 {step['step_name']} 被禁用，状态: {step['status']}")
        
        # 当测试计划状态为通过且步骤状态为失败时，就将计划状态改为失败
        print('\t')
        if run_status != FAILED and step.get('status') == FAILED:
            run_status = FAILED
            print(f"由于步骤 {step['step_name']} 失败，整体状态设为失败")
    
    # 这里不再在内存中计算成功率，而是等所有步骤执行完毕后从数据库查询
    print(f"步骤组执行完成 - 总状态: {'成功' if run_status == SUCCESS else '失败'}")
    
    return run_status, step_data


"""
执行api用例的主方法
执行测试计划：case_data={case_id:[step1,step2,step3]}
实时调试/步骤中计划：case_data=[step1,step2,step3]
批量执行：case_data=[step1,step2,step3]（新增支持）
temp_params为空的话则查询用户的参数来测试。
"""
def run_api_case_func(case_data, user_id, cfg_data=None, temp_params=None):
    # 延迟导入避免循环引用
    from .viewDef import ApiCasesActuator
    
    res_step_objs, res_case_objs = [], []
    actuator_obj = ApiCasesActuator(user_id, cfg_data=cfg_data, temp_params=temp_params)
    thread = MyThread(target=monitor_interrupt, args=[user_id, actuator_obj])
    thread.start()

    # 开始执行case_data
    if isinstance(case_data, list) and len(case_data) > 0:
        first_step = case_data[0] if case_data else {}
        case_id = first_step.get('case_id', 'unknown')

        print(f'这是{case_id}号用例,正在执行中...')
        start_time = datetime.datetime.now()
        case_objs = ApiCase.objects.filter(id=case_id).first()
        if case_objs:
            print('标记用例任务执行状态为running')
            case_objs.status = RUNNING
            case_objs.save(update_fields=['status'])
        
        report_dict = {
            'envir': actuator_obj.envir, 
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'steps': []
        }
        actuator_obj.base_params_source['case_id'] = case_id
        
        # 执行步骤组
        case_status, step_data = run_step_groups(actuator_obj, case_data)
        report_dict['steps'] = step_data
        
        # 从数据库中查询该用例的所有步骤的最新状态
        db_steps = ApiCaseStep.objects.filter(case_id=case_id)
        total_steps = db_steps.count()
        enabled_steps = db_steps.filter(enabled=True)
        enabled_step_count = enabled_steps.count()
        success_steps = enabled_steps.filter(status=SUCCESS)
        success_count = success_steps.count()
        
        # 计算成功率百分比
        if enabled_step_count > 0:
            success_rate = (success_count / enabled_step_count) * 100
        else:
            success_rate = 0
            
        # 添加统计数据到报告
        report_dict['statistics'] = {
            'total_steps': total_steps,
            'enabled_steps': enabled_step_count,
            'success_steps': success_count,
            'success_rate': round(success_rate, 2),  # 保留两位小数
            'success_rate_str': f"{round(success_rate, 2)}%"  # 带百分号的字符串形式
        }
        print(f"步骤成功率(数据库查询): {success_count}/{enabled_step_count} = {round(success_rate, 2)}%")

        print(f'开始存储用例组{case_id}所有步骤执行的结果\t')
        for step in step_data:
            # 过滤掉不属于ApiCaseStep模型的字段
            valid_fields = {
                'id', 'type', 'enabled', 'step_name', 'step_order', 'status', 
                'retried_times', 'controller_data', 'params', 'results', 
                'timeout', 'source'
            }
            filtered_step = {k: v for k, v in step.items() if k in valid_fields}
            
            # 将执行结果(data字段)存储到results字段中
            if 'data' in step and step['data']:
                filtered_step['results'] = step['data']

            
            # 正确设置外键关系，使用case而不是case_id
            if 'id' in filtered_step:
                # 如果有ID，说明是更新现有记录
                step_obj = ApiCaseStep(id=filtered_step['id'])
                for field, value in filtered_step.items():
                    if field != 'id' and field != 'case_id':  # 避免设置case_id字段
                        setattr(step_obj, field, value)
                # 确保case关系正确
                step_obj.case_id = case_id
                res_step_objs.append(step_obj)
            else:
                # 新记录，直接设置case_id
                step_obj = ApiCaseStep(case_id=case_id)
                for field, value in filtered_step.items():
                    if field != 'case_id':  # 避免重复设置case_id
                        setattr(step_obj, field, value)
                res_step_objs.append(step_obj)
        
        # 先保存步骤结果到数据库，以便后续查询统计
        print('先保存步骤执行结果到数据库...')
        # 创建一个临时的模型对象列表用于批量更新
        temp_step_objs = []
        for step_obj in res_step_objs:
            if hasattr(step_obj, 'case_id') and step_obj.case_id == case_id:
                temp_step_objs.append(step_obj)
        
        # 如果有步骤结果，立即保存
        if temp_step_objs:
            # 使用bulk_update批量更新步骤的状态和结果
            ApiCaseStep.objects.bulk_update(temp_step_objs, fields=['status', 'results'])
            print(f'成功保存 {len(temp_step_objs)} 个步骤的执行结果')
        
        end_time = datetime.datetime.now()
        report_dict['spend_time'] = format((end_time - start_time).total_seconds(), '.1f')
        if actuator_obj.status in (INTERRUPT, FAILED_STOP):
            case_status = actuator_obj.status
        res_case_objs.append(
            ApiCase(id=case_id, status=case_status, latest_run_time=end_time, report_data=report_dict))
        print(f'已完成{case_id}号用例的执行')
    
    else:
        print("警告：未识别的case_data格式或空数据")
        
    save_results( res_case_objs)
    
    # 确保执行状态设置为WAITING，通知监控线程可以终止
    UserCfg.objects.filter(user_id=user_id).update(exec_status=WAITING)
    
    # 构建返回结果
    result = {
        'cases': []
    }
    
    # 从数据库中获取最新的用例状态和报告数据
    for case_obj in res_case_objs:
        # 获取数据库中最新的用例数据
        fresh_case = ApiCase.objects.filter(id=case_obj.id).values('id', 'status', 'report_data').first()
        if fresh_case and fresh_case['report_data'] and 'statistics' in fresh_case['report_data']:
            result['cases'].append({
                'id': fresh_case['id'],
                'status': fresh_case['status'],
                'statistics': fresh_case['report_data'].get('statistics', {}),
                'steps': fresh_case['report_data'].get('steps', []),
                'spend_time': fresh_case['report_data'].get('spend_time', 0)
            })
    
    print('执行完成，返回结果')
    return result
