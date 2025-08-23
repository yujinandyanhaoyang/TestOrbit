from django.db import IntegrityError
from django.db.models import Value, F, Q
from django.db.models.functions import Concat
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apiData.models import ApiCase, ApiModule, ApiCaseStep, ApiForeachStep
from apiData.serializers import ApiCaseListSerializer, ApiDataListSerializer
from apiData.views.viewDef import save_step, parse_api_case_steps, run_api_case_func, ApiCasesActuator, go_step, monitor_interrupt
from utils.comDef import MyThread
from utils.constant import DEFAULT_MODULE_NAME, USER_API, API, FAILED, API_CASE, API_FOREACH, SUCCESS, RUNNING,  WAITING
from utils.diyException import CaseCascaderLevelError
from utils.paramsDef import set_user_temp_params
from utils.report import get_api_case_step_count, report_case_count, init_step_count
from utils.views import LimView
from config.models import Environment
from user.models import UserCfg

"""
用例步骤相关操作
"""

class ApiViews(LimView):
    queryset = ApiCaseStep.objects.all().select_related('case')
    serializer_class = ApiDataListSerializer
    filterset_fields = ('case_id', 'name', 'status', 'method')
    ordering_fields = ('name',)

    #  获取步骤详情
    def get(self, request, *args, **kwargs):
        req_params = request.query_params.dict()
        api_id, is_case = req_params.get('id'), req_params.get('is_case')
        print(f'查看当前测试步骤的详情信息：api_id: {api_id}')
        if api_id:  # 传递了case_id代表查详情
            extra_annotate, extra_fields = {}, []
            if not is_case:  # 代表需要接口的default测试数据
                extra_annotate, extra_fields = {}, ('params',)
            api_data = ApiCaseStep.objects.filter(id=api_id).annotate(
                api_id=F('id'), load_name=Concat('env_id__name', Value('-'), 'name', Value('-'), 'path'),
                **extra_annotate).values('api_id', 'name', 'load_name', 'path', 'timeout',
                                         'method', 'env_id', 'source', *extra_fields).first()
            if not api_data:
                return Response(data={'msg': '请求接口已被删除！请重新选择！'}, status=status.HTTP_400_BAD_REQUEST)
            return Response(data=api_data)
        return self.list(request, *args, **kwargs)

    # 新增或更新测试步骤
    def post(self, request, *args, **kwargs):
        req_data = request.data
        step = req_data['steps'][0]
        env_id = req_data.get('env_id')
        case_id = req_data.get('case_id')

        if step.get('step_id'):
            step_id = step['step_id']
            # 更新操作：通过case_id和step_id查找步骤
            step_checked = ApiCaseStep.objects.filter(case_id=case_id, id=step_id).first()

            if not step_checked:
                return Response(data={'msg': f'未找到对应的步骤！(case_id: {case_id}, step_id: {step_id})'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 新增操作：创建新步骤
            step_id = None

        try:            
            used_step_id = save_step(step, step_id, env_id, case_id)  # 存储测试数据和基础测试用例
            
            # 根据操作类型提供更清晰的成功消息
            if step_id:
                operation_msg = f'步骤更新成功！(步骤 ID: {used_step_id})'
            else:
                operation_msg = f'步骤创建成功！(步骤 ID: {used_step_id})'
            print(operation_msg)
            
        except IntegrityError as e:
            # 简化错误处理：只处理真正的完整性错误，不限制重复步骤创建
            operation_desc = "更新" if step_id else "创建"
            return Response(data={'msg': f'{operation_desc}步骤时发生数据库约束错误: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # print(f"Exception: {str(e)}")
            operation_desc = "更新" if step_id else "创建"
            return Response(data={'msg': f'{operation_desc}步骤时出错: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={'msg': operation_msg, 'data': {'step_id': used_step_id}})

    

@api_view(['GET'])
def search_api(request):
    """
    搜索接口
    """
    req_params = request.query_params.dict()
    case_data = ApiCaseStep.objects.filter(
        Q(name__icontains=req_params['search']) | Q(path__icontains=req_params['search'])).annotate(
        api_id=F('id'), value=Concat('case__name', Value('-'), 'name', Value('-'), 'path', Value('-'), 'method'),
        label=Concat('case__name', Value('-'), 'name', Value('-'), 'path', Value('-'), 'method')).values(
        'value', 'label', 'api_id')
    return Response(data=case_data)


@api_view(['POST'])
def run_api_cases(request):
    """
    执行Api测试用例
    """
    user_id, envir = request.user.id, request.data['envir']
    case_data = parse_api_case_steps(request.data['case'])
    UserCfg.objects.update_or_create(user_id=user_id, defaults={'exec_status': RUNNING, 'envir_id': envir})
    try:
        res = run_api_case_func(case_data, user_id, cfg_data={'envir_id': request.data['envir']})
        UserCfg.objects.filter(user_id=user_id).update(exec_status=WAITING)
        set_user_temp_params(res['params_source'], user_id)
    except Exception as e:
        return Response(data={'msg': f"执行异常：{str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    return Response(data={'msg': "执行完成！"})

@api_view(['POST'])
def run_api_case_step(request):
    """
    执行api用例步骤
    """
    req_data = request.data
    user_id = request.user.id
    actuator_obj = ApiCasesActuator(user_id)
    s_type = req_data['type']
    try:
        UserCfg.objects.filter(user_id=user_id).update(exec_status=RUNNING)
        if s_type in (API_CASE, API_FOREACH):
            thread = MyThread(target=monitor_interrupt, args=[user_id, actuator_obj])
            thread.start()
        res = go_step(actuator_obj, req_data, i=0)
    except CaseCascaderLevelError as e:
        return Response(data={'status': FAILED, 'msg': str(e)})
    res_msg = ''
    if res['status'] != SUCCESS:
        if s_type in (API_CASE, API_FOREACH):
            res_msg = '请前往步骤详情中查看失败或跳过原因！'
        elif isinstance(res['data'], dict):
            res_msg = res['data'].get('msg')
        else:
            res_msg = str(res['data'])
    UserCfg.objects.filter(user_id=user_id).update(exec_status=WAITING)
    set_user_temp_params(actuator_obj.params_source, request.user.id)
    return Response({'msg': res_msg, 'data': {'status': res['status'], 'retried_times': res.get('retried_times'),
                                                 'data': res.get('data')}})


@api_view(['GET'])
def get_api_report(request):
    """
    获取api报告
    """
    case_data = ApiCase.objects.filter(
        id=request.query_params['case_id']).values('name', 'report_data').first() or {}
    report_data = case_data.get('report_data')
    if report_data:
        envir_name = Environment.objects.filter(id=report_data['envir']).values_list('name', flat=True).first()
        report_data.update(
            {'case_count': 0, 'envir_name': envir_name, 'name': case_data['name'], 'step_count': init_step_count(),
             'cases': {}})
        get_api_case_step_count(report_data['steps'], report_data)
        if report_cases := report_data['cases']:
            case_ids = list(report_cases.keys())
            _data = ApiCase.objects.filter(id__in=case_ids).values('id', 'name')
            case_name_dict = {v['id']: v['name'] for v in _data}
            report_data['case_count'] = len(case_ids)
            try:
                report_case_count(case_ids, report_cases, case_name_dict, report_data)
            except Exception as e:
                return Response(data={'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response(data=report_data)
        return Response(data={'msg': "该用例没有步骤！"}, status=status.HTTP_400_BAD_REQUEST)
    return Response(data={'msg': "无该用例的测试报告！"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def test_api_data(request):
    """
    调试API接口请求。运行单步骤用例
    """
    # print("调试API接口请求。运行单步骤用例")
    req_data, user_id = request.data, request.user.id
    actuator_obj = ApiCasesActuator(user_id)
    req_data['type'] = API
    res = go_step(actuator_obj, req_data, i=0)
    UserCfg.objects.filter(user_id=user_id).update(exec_status=WAITING)
    set_user_temp_params(actuator_obj.params_source, request.user.id)
    return Response(res.get('data', {}))


@api_view(['GET'])
def search_case_by_api(request):
    """
    查询使用了指定接口的用例
    """
    if 'api_id' in request.query_params:
        api_id = int(request.query_params['api_id'])
        case_ids = list(ApiCaseStep.objects.filter(api_id=api_id).values_list('case_id', flat=True))
        case_ids += list(ApiForeachStep.objects.filter(api_id=api_id).annotate(case_id=F('step__case_id')).values_list(
            'case_id', flat=True))
        serializer = ApiCaseListSerializer(
            ApiCase.objects.filter(id__in=set(case_ids)), many=True, context={'request': request})
        ser_data = serializer.data
        return Response({'data': ser_data, 'total': len(ser_data)})
    return Response({'data': {}})
