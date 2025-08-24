from django.db import IntegrityError
from django.db.models import Value, F, Q
from django.db.models.functions import Concat
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apiData.models import ApiCase,  ApiCaseStep, ApiForeachStep
from apiData.serializers import ApiCaseListSerializer, ApiDataListSerializer
from apiData.views.viewDef import  parse_api_case_steps, run_api_case_func, ApiCasesActuator, go_step, monitor_interrupt
from utils.comDef import MyThread
from utils.constant import DEFAULT_MODULE_NAME, USER_API, API, FAILED, API_CASE, API_FOREACH, SUCCESS, RUNNING,  WAITING
from utils.diyException import CaseCascaderLevelError
from utils.paramsDef import set_user_temp_params
from utils.report import get_api_case_step_count, report_case_count, init_step_count
from utils.views import LimView
from config.models import Environment
from user.models import UserCfg




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



