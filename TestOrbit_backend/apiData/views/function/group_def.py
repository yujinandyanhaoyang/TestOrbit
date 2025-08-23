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





# 复制用例组
def copy_cases_func(request, case_model, step_model, foreach_step_model=None):
    """
    复制用例方法
    """

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
