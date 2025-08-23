import datetime

from django.db import IntegrityError, transaction
from django.db.models import  Max
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apiData.models import ApiCaseModule, ApiCase, ApiModule, ApiCaseStep, ApiForeachStep
from apiData.serializers import ApiCaseListSerializer, ApiCaseSerializer, ApiCaseDetailSerializer
from apiData.views.viewDef import parse_create_foreach_steps, copy_cases_func, save_step
from utils.comDef import get_module_related, get_case_sort_list
from utils.constant import API,  API_CASE, API_FOREACH,WAITING, INTERRUPT, USER_API
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
        
        # step_order查关联接口的时候用
        # 通过step_order查找步骤
        # 每个具体步骤通过case_id+step_order唯一确定
        case_id, step_order = req_params.get('id'), req_params.get('step_order')

        if case_id:  # 有case_id代表请求详情


            instance = ApiCase.objects.defer('report_data').get(id=case_id)
            context = {'step_order': step_order, 'user_id': request.user.id}
            
            serializer = ApiCaseDetailSerializer(instance, context=context)
            # print('✅ 序列化器创建完成')

            # print("📤 开始数据序列化...")
            serialized_data = serializer.data

            # print('✅ 序列化完成!')
            
            return Response(data=serialized_data)
        
        return self.list(request, *args, **kwargs)

    # 新增用例组方法
    def post(self, request, *args, **kwargs):
        """
        处理用例组的新增和更新，包括所有步骤的保存
        """
        print('开始保存用例组\t')
        req_data = request.data
        case_id  = req_data.get('id')
        env_id = req_data.get('env_id')
        steps = req_data.get('steps')
        for_next_id =  None
        save_case_data = {field: req_data.get(field) for field in ('name', 'module_id', 'remark')
                          if field in req_data}
        try:
            with transaction.atomic():
                if case_id:  # case_id存在，代表修改用例组
                    print(f'存在case_id:{case_id},当前为修改用例组')
                    save_case_data.update({'updater_id': request.user.id, 'updated': datetime.datetime.now()})
                    ApiCase.objects.filter(id=case_id).update(**save_case_data)
                else:
                    case = ApiCase.objects.create(**save_case_data)
                    case_id = case.id
                
                steps_objs, foreach_steps = [], []
                have_foreach = False
                
                print('进入保存用例步骤\t')
                for step in steps:
                    s_type = step['type']
                    
                    if s_type == API:

                        # 检查是否存在id，决定是更新还是创建
                        if step.get('id'):
                            step_id = step['id']
                        else:
                            step_id = None      
                        used_step_id = save_step(step, step_id, env_id, case_id)  # 存储测试数据和基础测试用例

                        # 暂时不考虑其他类型
                    # elif s_type == API_CASE:
                    #     # 用例引用类型步骤
                    #     step_params = step.get('params', {})
                    #     step_basic_data['quote_case_id'] = step_params.get('case_related', [])[-1] if step_params.get('case_related') else None
                    #     steps_objs.append(ApiCaseStep(**step_basic_data))
                        
                    # elif s_type == API_FOREACH:
                    #     # 循环步骤
                    #     have_foreach = True
                    #     foreach_steps.append({
                    #         'steps': step.get('params', {}).get('steps', []), 
                    #         'step_order': step_index + 1
                    #     })
                    #     steps_objs.append(ApiCaseStep(**step_basic_data))
                    # else:
                    #     # 其他类型步骤（var, header, host, sql等）
                    #     steps_objs.append(ApiCaseStep(**step_basic_data))
                
                
                
                # 处理循环步骤
                if have_foreach:
                    for_next_id = 1  # 循环步骤从1开始编号
                    case_steps = ApiCaseStep.objects.filter(case_id=case_id, type=API_FOREACH)
                    step_mapping = {step.step_order: step for step in case_steps}
                    
                    save_step_objs = []
                    for foreach_step in foreach_steps:
                        parent_step = step_mapping.get(foreach_step['step_order'])
                        if parent_step:
                            for_next_id = parse_create_foreach_steps(
                                save_step_objs, foreach_step['steps'], parent_step, for_next_id)
                    ApiForeachStep.objects.bulk_create(save_step_objs)
        except Exception as e:
            import traceback
            error_info = traceback.format_exc()
            print(f'\n错误发生在第 {e.__traceback__.tb_lineno} 行')
            print(f'错误类型: {type(e).__name__}')
            print(f'错误信息: {str(e)}')
            print(f'完整的错误堆栈:\n{error_info}')
            
            if '1062' in str(e):
                return Response(data={'msg': '该用例名已存在！'}, status=status.HTTP_400_BAD_REQUEST)
            return Response(data={'msg': f'保存出错：{str(e)}\n详细信息：{error_info}'}, status=status.HTTP_400_BAD_REQUEST)
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
