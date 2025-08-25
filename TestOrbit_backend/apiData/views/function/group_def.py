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
    case_obj = case_model.objects.get(id=req_data['case_id'])
    case_obj.creater_id = request.user.id
    case_obj.id = None
    case_obj.status = WAITING
    case_obj.name = case_obj.name + '-COPY'
    case_steps = step_model.objects.filter(case_id=req_data['case_id']).values()
    case_obj.save()
    step_objs = []
    foreach_steps_obj = []
    next_id = (ApiCaseStep.objects.aggregate(Max('id')).get('id__max') or 0) + 1
    for step in case_steps:
        step['case_id'] = case_obj.id
        old_step_id = step.pop('id')
        step['id'] = next_id
        step.pop('results', None)
        step_objs.append(step_model(**step))
        # print('ada', step)
        if step['type'] == API_FOREACH:
            for for_step in ApiForeachStep.objects.filter(step_id=old_step_id).values():
                for_step.pop('id')
                for_step['step_id'] = next_id
                print('fa', for_step)
                foreach_steps_obj.append(ApiForeachStep(**for_step))
        next_id += 1
    step_model.objects.bulk_create(step_objs)
    if foreach_steps_obj:
        ApiForeachStep.objects.bulk_create(foreach_steps_obj)
    return Response(data={'msg': "复制成功！"})


"""
转化API计划步骤
is_step:false代表非步骤中的用例，即外层计划列表中选中执行的用例
"""
def parse_api_case_steps(case_ids=None, is_step=False):
    step_data = []
    if case_ids:
        # 参数现在通过关联的ApiData.params获取
        step_data = list(ApiCaseStep.objects.filter(case_id__in=case_ids).select_related(
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
def save_results(step_data, case_data):
    ApiCase.objects.bulk_update(case_data, fields=('status', 'report_data', 'latest_run_time'))
    ApiCaseStep.objects.bulk_update(step_data, fields=('status', 'results', 'params'))



"""
执行步骤合集
"""
def run_step_groups(actuator_obj, step_data, prefix_label='', cascader_level=0, i=0):
    # 默认测试是通过的
    run_status = SUCCESS
    print('开始使用run_step_groups函数执行步骤合集')
    for step in step_data:

        # 往step中添加step_id，方便后续引用
        step['step_id'] = step.get('id')
        step_id = step.get('id')
        s_type = step['type']

        if step.get('enabled'):
            params = {'actuator_obj': actuator_obj, 'step_id': step_id, 'prefix_label': prefix_label,
                      'i': i}
            if s_type in (API_CASE, API_FOREACH):
                params['cascader_level'] = cascader_level + 1
            # print(f'params:{params}\t')
            res = go_step(**params)
            # print(f'{step["step_name"]}步骤执行结果: {res}')
            step.update(res)
        else:
            step['status'] = DISABLED
        # step.update({'status': res['status'], 'results': res.get('results')})
        # 当测试计划状态为通过且步骤状态为失败时，就将计划状态改为失败
        print('\t')
        if run_status != FAILED and step['status'] == FAILED:
            run_status = FAILED
    return run_status, step_data


"""
执行api用例的主方法
执行测试计划：case_data={case_id:[step1,step2,step3]}
实时调试/步骤中计划：case_data=[step1,step2,step3]
temp_params为空的话则查询用户的参数来测试。
"""
def run_api_case_func(case_data, user_id, cfg_data=None, temp_params=None):
    # 延迟导入避免循环引用
    from .viewDef import ApiCasesActuator
    
    res_step_objs, res_case_objs = [], []
    actuator_obj = ApiCasesActuator(user_id, cfg_data=cfg_data, temp_params=temp_params)
    thread = MyThread(target=monitor_interrupt, args=[user_id, actuator_obj])
    thread.start()
    if isinstance(case_data, dict):
        for case_id, v in case_data.items():
            print(f'这是{case_id}号用例')
            start_time = datetime.datetime.now()
            case_objs = ApiCase.objects.filter(id=case_id).first()
            if case_objs:
                print('标记用例任务执行状态为running')
                case_objs.status = RUNNING
                case_objs.save(update_fields=['status'])
            report_dict = {'envir': actuator_obj.envir, 'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                           'steps': []}
            actuator_obj.base_params_source['case_id'] = case_id
            # 默认测试是通过的
            case_status, step_data = run_step_groups(actuator_obj, v)
            # print('步骤执行结果:', step_data)

            report_dict['steps'] = step_data

            print(f'开始存储用例组{case_id}所有步骤执行的结果\t')
            for step in step_data:
                # 过滤掉不属于ApiCaseStep模型的字段
                valid_fields = {
                    'id', 'type', 'enabled', 'step_name', 'step_order', 'status', 
                    'retried_times', 'controller_data', 'params', 'results', 
                    'timeout', 'source', 'case_id'
                }
                filtered_step = {k: v for k, v in step.items() if k in valid_fields}
                
                # 将执行结果(data字段)存储到results字段中
                if 'data' in step and step['data']:
                    filtered_step['results'] = step['data']
                
                # 确保case_id字段存在
                filtered_step['case_id'] = case_id
                res_step_objs.append(ApiCaseStep(**filtered_step))
            end_time = datetime.datetime.now()
            report_dict['spend_time'] = format((end_time - start_time).total_seconds(), '.1f')
            if actuator_obj.status in (INTERRUPT, FAILED_STOP):
                case_status = actuator_obj.status
            res_case_objs.append(
                ApiCase(id=case_id, status=case_status, latest_run_time=end_time, report_data=report_dict))
            print(f'已完成{case_id}号用例的执行')
        save_results(res_step_objs, res_case_objs)
        
        # 确保执行状态设置为WAITING，通知监控线程可以终止
        UserCfg.objects.filter(user_id=user_id).update(exec_status=WAITING)
        
        return {'params_source': actuator_obj.params_source}

