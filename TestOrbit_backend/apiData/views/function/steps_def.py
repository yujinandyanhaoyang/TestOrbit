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
# 移除对 ProjectEnvirData 的导入，使用 Environment
from config.models import Environment
from user.models import UserCfg, UserTempParams


def create_api(step,env_id,case_id):
    """
    创建自定义Api用例基础数据
    """
    # print("正在调用ApiCaseStep.objects.create函数创建新 API")
    # print("正在创建新的 API...")
    step = ApiCaseStep.objects.create(
        type=step['type'], 
        enabled=step["enabled"],
        step_name=step['step_name'], 
        step_order=step['step_order'],
        params=step['params'],
        results=step['results'],
        timeout=30,  # 设置默认值
        source=USER_API,
        env_id=env_id, 
        case_id=case_id,)
    print(f"创建的 API ID 为：{step.id}")
    return step.id


def update_step(step, step_id, env_id):
    """
    更新自定义Api用例基础数据
    """
    ApiCaseStep.objects.filter(id=step_id).update(
        type=step['type'], 
        enabled=step["enabled"],
        step_name=step['step_name'], 
        step_order=step['step_order'],
        params=step['params'],
        results=step['results'],
        env_id=env_id)
    print(f"{step_id} 更新成功")


def save_step(step, step_id, env_id, case_id):
    """
    创建用例步骤
    """
    print(f"已进入 save_step 函数，参数如下：")
    if step_id:
        print(f"更新步骤，step_id: {step_id}")
        update_step(step, step_id, env_id)
    else:
        print(f"创建新步骤")
        step_id = create_api(step,env_id,case_id)
    return step_id


# 步骤执行函数,调用ApiCasesActuator.api方法运行具体用例
def go_step(actuator_obj, step, i=0, prefix_label='', **extra_params):
    print("\n" + "-"*50)
    print("🔍 go_step函数开始执行")

    # 优先检查当前步骤已保存
    step_id = step.get('step_id')
    if step_id:
        #检查这个step_id在数据库中是否存在
        CaseStep = ApiCaseStep.objects.filter(id=step['step_id']).first()
        if not CaseStep:
            return {'status': FAILED}
    else:
        # 步骤未保存，返回错误状态
        return {'status': FAILED}

    # 获取步骤类型
    s_type = step['type']
    
    # 检查是否需要中断执行
    if actuator_obj.status in (INTERRUPT, FAILED_STOP):
        print("⚠️ 执行已被中断，跳过执行")
        return {'status': SKIP, 'data': '执行被中断！' if s_type not in (API_CASE, API_FOREACH) else None}
    
    params = {'step': step, 'i': i, 'prefix_label': prefix_label, **extra_params}
    # 获取控制器数据
    controller_data = step.get('controller_data') or {}
    print(f"🎮 控制器数据: {controller_data}")
    
    # 设置重试次数和间隔
    retry_times = controller_data.get('re_times', 0) if s_type not in (API_CASE, API_FOREACH) else 0
    retry_interval = controller_data.get('re_interval', 0)
    execute_on = controller_data.get('execute_on', '')
    sleep_time = controller_data.get('sleep')

    # 初始化结果
    res = {'status': SUCCESS, 'data': ''}

    # 检查是否有执行条件
    if execute_on:
        print("🔍 检查执行条件...")
        try:
            condition_result = run_params_code(execute_on, copy.deepcopy(actuator_obj.default_var), i)
            if not condition_result:
                print("⚠️ 执行条件不满足，跳过执行")
                return {'status': SKIP, 'data': '【控制器】执行条件不满足！'}
            print("✅ 执行条件满足，继续执行")
        except Exception as e:
            print(f"❌ 执行条件检查出错: {str(e)}")
            if actuator_obj.failed_stop:
                actuator_obj.running_status = INTERRUPT
                print("⛔ 已设置中断标志")
            return {'status': FAILED, 'data': '【控制器】' + str(e)}
    
    # 执行前等待
    if sleep_time:
        print(f"⏱️ 执行前等待 {sleep_time} 秒...")
        time.sleep(sleep_time)
    
    # 执行步骤（包含重试逻辑）
    print("\n🚀 开始执行步骤...")
    for j in range(retry_times + 1):
        # print(f"🔄 第 {j+1}/{retry_times+1} 次尝试执行: {step.get('step_name', '未命名步骤')}")
        try:
            # 通过反射调用对应类型的方法
            print(f"📡 调用 actuator_obj.{s_type} 方法")

            # 使用getters动态获取方法,执行actuator_obj.{s_type} 方法获取返回结果
            method_result = getattr(actuator_obj, s_type)(**params)
            res = method_result or {'status': SUCCESS}
            
            # 对于SQL类型特殊处理
            if s_type == API_SQL and 'data' in res:
                print("🗄️ SQL执行结果中移除data字段")
                res.pop('data', None)
                
            
        except Exception as e:
            # 捕获执行异常
            print(f"❌ 执行出错: {str(e)}")
            res = {'status': FAILED, 'data': str(e)}
            
        # 处理失败重试逻辑
        if res['status'] == FAILED:
            if j < retry_times:
                print(f"⚠️ 执行失败，将在 {retry_interval} 秒后重试")
                time.sleep(retry_interval)
            else:
                print("❌ 所有重试都失败了")
        else:
            print("✅ 执行成功")
            break
    
    # 记录重试次数
    res['retried_times'] = j
    print(f"📝 总执行次数: {j+1}")
    
    # 日志处理逻辑
    if actuator_obj.only_failed_log and res['status'] in (SUCCESS, SKIP) and s_type != API_CASE:
        print("📝 仅记录失败日志模式，不记录本次成功执行")
        return {'status': res['status'], 'retried_times': res['retried_times']}
    
    # 失败处理逻辑
    if res['status'] == FAILED:
        print("❌ 步骤执行失败")
        if actuator_obj.failed_stop:
            actuator_obj.status = FAILED_STOP
            print("⛔ 设置执行器状态为失败中断")

    # 保存运行结果
    CaseStep.results = res.get('data', {})
    CaseStep.save()

    print(f"🏁 go_step函数执行完成，返回状态: {res['status']}")
    print("-"*50 + "\n")
    return res
