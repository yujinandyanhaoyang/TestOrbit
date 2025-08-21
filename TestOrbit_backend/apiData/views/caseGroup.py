import datetime

from django.db import IntegrityError, transaction
from django.db.models import  Max
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apiData.models import ApiCaseModule, ApiCase, ApiModule,  ApiCaseStep, ApiForeachStep
from apiData.serializers import  ApiCaseListSerializer,  ApiCaseSerializer, ApiCaseDetailSerializer
from apiData.views.viewDef import  parse_create_foreach_steps,  copy_cases_func
from utils.comDef import get_module_related, get_case_sort_list
from utils.constant import API,  API_CASE, API_FOREACH,WAITING, INTERRUPT
from utils.views import LimView
from user.models import UserCfg

"""
用例组相关操作
"""

class ApiCaseViews(LimView):
    queryset = ApiCase.objects.order_by(
        'position', '-updated').select_related('creater', 'updater')
    query_only_fields = (
        'id', 'name', 'creater', 'updater', 'updated', 'created', 'status', 'latest_run_time')
    serializer_class = {'list': ApiCaseListSerializer, 'detail': ApiCaseSerializer}
    diy_search_fields = ('name',)
    filterset_fields = ('module_id', 'status', 'is_deleted')
    ordering_fields = ('created', 'name', 'updated', 'latest_run_time')

    #获取用例组详情
    def get(self, request, *args, **kwargs):
        req_params = request.query_params.dict()
        # api_id查关联接口的时候用
        case_id, api_id = req_params.get('id'), req_params.get('api_id')
        if case_id:  # 有case_id代表请求详情
            instance = ApiCase.objects.defer('report_data').get(id=case_id)
            serializer = ApiCaseDetailSerializer(instance, context={'api_id': api_id, 'user_id': request.user.id})
            return Response(data=serializer.data)
        return self.list(request, *args, **kwargs)

    # 新增用例组方法
    def post(self, request, *args, **kwargs):
        req_data = request.data
        case_id, steps, for_next_id = req_data.get('id'), req_data.get('steps'), None
        save_case_data = {field: req_data.get(field) for field in ('name', 'module_id', 'remark')
                          if field in req_data}
        try:
            with transaction.atomic():
                if case_id:  # 代表修改用例
                    save_case_data.update({'updater_id': request.user.id, 'updated': datetime.datetime.now()})
                    ApiCase.objects.filter(id=case_id).update(**save_case_data)
                else:
                    case = ApiCase.objects.create(**save_case_data)
                    case_id = case.id
                steps_objs, foreach_steps = [], []
                have_foreach = False
                for step in steps:
                    step.update({'case_id': case_id, 'retried_times': 0})
                    step.pop('id', None)
                    step.pop('is_relation', None)
                    if (s_type := step['type']) == API:
                        step['api_id'] = step['params']['api_id']
                    elif s_type == API_CASE:
                        step['quote_case_id'] = step['params']['case_related'][-1]
                    elif s_type == API_FOREACH:
                        have_foreach = True
                        foreach_steps.append({'steps': step['params'].pop('steps')})
                    steps_objs.append(ApiCaseStep(**step))
                if have_foreach:
                    for_next_id = (ApiForeachStep.objects.aggregate(Max('id')).get('id__max') or 0) + 1
                ApiCaseStep.objects.filter(case_id=case_id).delete()
                ApiCaseStep.objects.bulk_create(steps_objs)
                if have_foreach:
                    foreach_step_ids = ApiCaseStep.objects.filter(
                        case_id=case_id, type=API_FOREACH).values_list('id', flat=True).order_by('id')
                    for i, foreach_step in enumerate(foreach_steps):
                        foreach_step['step_id'] = foreach_step_ids[i]
                    save_step_objs = []
                    for foreach_step in foreach_steps:  # foreach_step=[...'steps':{xx}]
                        for_next_id = parse_create_foreach_steps(
                            save_step_objs, foreach_step['steps'], foreach_step['step_id'], for_next_id)
                    ApiForeachStep.objects.bulk_create(save_step_objs)
        except Exception as e:
            print('err', e.__traceback__.tb_lineno)
            if '1062' in str(e):
                return Response(data={'msg': '该用例名已存在！'}, status=status.HTTP_400_BAD_REQUEST)
            return Response(data={'msg': '保存出错：' + str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'msg': '保存成功！', 'case_id': case_id})

    #删除用例组方法
    def delete(self, request, *args, **kwargs):
        if request.query_params.get('real_delete'):
            return self.destroy(request, *args, **kwargs)

        if api_step := ApiCaseStep.objects.filter(quote_case_id=request.query_params['id']).first():
            return Response({'msg': f'该用例已被【{api_step.case.name}】用例引用，无法删除！'},
                            status=status.HTTP_400_BAD_REQUEST)
        elif foreach_step := ApiForeachStep.objects.filter(quote_case_id=request.query_params['id']).first():
            return Response({'msg': f'该用例已被【{foreach_step.step.case.name}】用例的循环控制步骤引用，无法删除！'},
                            status=status.HTTP_400_BAD_REQUEST)

        api_case_name = f"{self.get_object().name}{str(timezone.now().timestamp())}"
        request.data.clear()
        request.data.update({'name': api_case_name, 'is_deleted': True, 'updater': request.user.id})
        return self.patch(request, *args, **kwargs)


@api_view(['POST'])
def stop_casing(request):
    """
    中断测试
    """
    UserCfg.objects.filter(user_id=request.user.id).update(exec_status=INTERRUPT)
    return Response({'msg': '中断成功，请等待几秒后刷新列表查看！'})


@api_view(['POST'])
def copy_step_to_other_case(request):
    """
    复制测试用例中的某个步骤到其他测试用例下
    """
    params = request.data
    ApiCaseStep.objects.create(
        step_name=params['step_name'], type=params['type'],
        case_id=params['to_case'], status=WAITING, api_id=params.get('params', {}).get('api_id'),
        enabled=True, controller_data=params.get('controller_data', {}), params=params['params'])
    ApiCase.objects.filter(id=params['to_case']).update(updater_id=request.user.id, updated=datetime.datetime.now())
    return Response({'msg': '复制成功！'})


@api_view(['POST'])
def copy_cases(request):
    """
    复制用例
    """
    return copy_cases_func(request, ApiCase, ApiCaseStep)


@api_view(['POST'])
def merge_cases(request):
    """
    合并用例
    """
    req_data = request.data
    try:
        cases = ApiCase.objects.filter(id__in=req_data['case_ids']).values('id', 'name', 'module_id')
        case_dict = {case['id']: case for case in cases}
        merge_case = ApiCase.objects.create(
            name=req_data['name'], creater_id=request.user.id, module_id=req_data['module_id'])
        step_objs = []
        for case_id in req_data['case_ids']:
            case = case_dict[case_id]
            mod_related = get_module_related(ApiCaseModule, case['module_id'], [case_id])
            step_objs.append(ApiCaseStep(
                step_name=case['name'], type=API_CASE, status=WAITING, case_id=merge_case.id,
                params={'case_related': mod_related}))
        ApiCaseStep.objects.bulk_create(step_objs)
    except IntegrityError as e:
        print(str(e))
        return Response(data={'msg': '该测试用例已存在！'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(data={'msg': "合并成功！"})



@api_view(['GET'])
def case_sort_list(request):
    """
    用例排序（简易）列表
    """
    return Response(get_case_sort_list(ApiCase, ApiModule, request))


@api_view(['POST'])
def set_case_position(request):
    """
    用例排序列表
    """
    case_objs = []
    for i, case in enumerate(request.data['cases']):
        case_objs.append(ApiCase(position=i, id=case['id']))
    ApiCase.objects.bulk_update(case_objs, fields=('position',))
    return Response({'msg': '修改成功'})


@api_view(['DELETE'])
def clean_deleted_cases(request):
    """
    清空回收站
    """
    ApiCase.objects.filter(is_deleted=True).delete()
    return Response({'msg': '清空成功！'})


@api_view(['DELETE'])
def delete_selected_cases(request):
    """
    删除选中的测试用例
    """
    ApiCase.objects.filter(id__in=request.data['ids']).update(is_deleted=True)
    return Response({'msg': '删除成功！'})
