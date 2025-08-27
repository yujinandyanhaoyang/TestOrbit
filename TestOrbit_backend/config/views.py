import datetime
import time

from django.db import transaction
from django.db.models import F, Value, JSONField
from django.db.models.functions import Concat
# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apiData.models import ApiModule, ApiCaseStep, ApiCase
from apiData.views.function.viewDef import ApiCasesActuator
from utils.comDef import db_connect, get_proj_envir_db_data, close_db_con
from utils.constant import API, DB, DEFAULT_MODULE_NAME, SUCCESS, API_HOST, API_SQL, VAR_PARAM
from utils.paramsDef import set_user_temp_params
from utils.views import View
from project.models import Project
from config.models import Environment, ProjectEnvironment, CaseEnvironment  # 移除 ProjectEnvirData 导入
from config.serializers import EnvironmentSerializer, CaseEnvironmentSerializer
from user.models import UserTempParams


class EnvironmentView(View):
    """
    环境配置视图类
    处理环境配置的创建、列表、修改和删除
    
    """
    serializer_class = EnvironmentSerializer
    queryset = Environment.objects.order_by('-created')

    @staticmethod
    def get_api_url_from_request(request):
        """从请求中提取 API URL"""
        url = request.data.get('url')
        
        # 尝试从 API 配置中提取 URL
        for key in request.data:
            if key.startswith('envir') and key.endswith('_api'):
                api_url = request.data[key]
                if not url and isinstance(api_url, str):
                    url = api_url
                    break
                    
        return url

    def post(self, request, *args, **kwargs):
        """创建新环境"""
        try:
            with transaction.atomic():
                # 提取 API URL
                url = self.get_api_url_from_request(request)
                
                # 创建环境记录
                environment = Environment.objects.create(
                    name=request.data['name'],
                    remark=request.data.get('remark'),
                    url=request.data.get('url') or url  # 优先使用请求中的 url，否则使用从 API 配置中提取的 url
                )
                
                # 注意：不再自动创建 ApiModule，因为环境不应该自动关联到特定项目的模块
                # 如果需要为特定项目创建模块，应该在项目管理中进行
        except Exception as e:
            if '1062' in str(e):
                return Response({'msg': '已存在同名环境！'}, status=status.HTTP_400_BAD_REQUEST, headers={})
            return Response(data={'msg': f"执行出错:{str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'msg': '创建成功！', 'id': environment.id})

    def patch(self, request, *args, **kwargs):
        """更新环境信息"""
        try:
            # 提取 API URL
            url = self.get_api_url_from_request(request)
            
            # 如果提供了 URL，更新到请求数据中
            if url and not request.data.get('url'):
                request.data['url'] = url
                
            # 使用父类的 partial_update 方法更新环境
            return self.partial_update(request, *args, **kwargs)
        except Exception as e:
            return Response(data={'msg': f"执行出错:{str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_project_envir_data(request):
    """
    获取项目环境配置
    
    技术债务清理：移除 ProjectEnvirData 依赖，直接使用 Environment
    现在所有项目可以访问所有环境
    """
    project_id = request.query_params.get('id')
    
    # 获取所有环境
    environments = Environment.objects.all().values('id', 'name', 'url')
    
    # 构造返回数据
    envir_data = []
    for env in environments:
        # 为每个环境构造一个基本的数据结构
        env_data = {
            'id': env['id'],
            'name': env['name'],
            'data': {
                'api': env['url'],  # 使用 url 字段作为 API 地址
                'db': {}  # 默认的空数据库配置
            }
        }
        envir_data.append(env_data)
    
    return Response(data=envir_data)


@api_view(['GET'])
def get_project_have_envir(request):
    """
    获取配置了指定环境参数的项目
    
    技术债务清理：移除 ProjectEnvirData 依赖，直接使用 Environment
    现在所有项目可以访问所有环境
    """
    _type = request.query_params['type']
    
    # 获取所有环境，并将它们都标记为可用（不禁用）
    environments = Environment.objects.all().values('id', 'name', 'url')
    pro_data = {env['id']: {'id': env['id'], 'name': env['name'], 'disabled': False} for env in environments}

    # 在新的业务逻辑下，所有环境都被视为可用
    if _type == API_HOST:
        # 所有有 URL 的环境都可用于 API_HOST
        for env_id, env_data in pro_data.items():
            env = next((e for e in environments if e['id'] == env_id), None)
            if env and env['url']:
                env_data['disabled'] = False
    elif _type == API_SQL:
        # 对于数据库连接，我们可能需要更复杂的逻辑
        # 这里简化处理，假设所有环境都支持默认数据库
        for env_id, env_data in pro_data.items():
            env_data['disabled'] = False
            # 为每个环境添加一个默认的数据库连接
            env_data['children'] = [{'id': 'default', 'name': 'default'}]
    
    return Response(list(pro_data.values()))


@api_view(['POST'])
def test_db_connect(request):
    """
    测试数据库连接
    """
    res = db_connect(request.data)
    if res['status'] == SUCCESS:
        res['db_con'].close()
        res['ssh_server'] and res['ssh_server'].close()
        return Response({'msg': '连接成功'})
    return Response({'msg': res['results']}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def get_proj_db_database(request):
    """
    获取数据库连接的所有数据库
    """
    db_data = get_proj_envir_db_data(request.data['db'], user_id=request.user.id)
    if db_data:
        res = db_connect(db_data)
        if res['status'] == SUCCESS:
            res['db_con'].execute('SHOW DATABASES')
            sql_data = [{'id': db['Database'], 'name': db['Database']} for db in res['db_con'].fetchall()]
            close_db_con(res)
            return Response(sql_data)
        return Response({'msg': res['results']}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'msg': '无效的连接！'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def run_sql(request):
    req_data, user_id = request.data, request.user.id
    case_obj = ApiCasesActuator(
        user_id, temp_params=UserTempParams.objects.filter(user_id=user_id, type=VAR_PARAM).values())
    res = case_obj.sql(step=req_data)
    if res['status'] == SUCCESS:
        set_user_temp_params(case_obj.params_source, user_id)
        return Response(res['data'])
    res['msg'] = res.pop('results')
    return Response(data=res, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_index_statistics(request):
    """
    获取首页统计数据
    """
    now_time = time.mktime(datetime.date.today().timetuple())

    res_data = {
        'project_new_count': 0, 'api_count': 0, 'api_new_count': 0, 'case_count': 0, 'case_new_count': 0,
        'api_data': {}, 'case_data': {}}
    proj_data = Environment.objects.values('id', 'created').order_by('-created')
    api_data = ApiCaseStep.objects.annotate(project_name=F('project__name')).values('created', 'project_name')
    case_data = ApiCase.objects.annotate(creater_name=Concat(
        'creater__real_name', Value('-'), 'creater__username')).filter(
        is_deleted=False).values('created', 'creater_name')

    res_data['project_count'] = len(proj_data)
    for proj in proj_data:
        if time.mktime(proj['created'].timetuple()) > now_time:
            res_data['project_new_count'] += 1
        else:
            break
    for api in api_data:
        if time.mktime(api['created'].timetuple()) > now_time:
            res_data['api_new_count'] += 1
        res_data['api_count'] += 1
        res_data['api_data'].setdefault(api['project_name'], 0)
        res_data['api_data'][api['project_name']] += 1
    res_data['api_data'] = [
        {'name': proj_name, 'count': res_data['api_data'][proj_name]} for proj_name in res_data['api_data'].keys()]
    for case in case_data:
        if time.mktime(case['created'].timetuple()) > now_time:
            res_data['case_new_count'] += 1
        res_data['case_count'] += 1
        res_data['case_data'].setdefault(case['creater_name'], 0)
        res_data['case_data'][case['creater_name']] += 1
    res_data['case_data'] = [
        {'name': c_name, 'count': res_data['case_data'][c_name]} for c_name in res_data['case_data'].keys()]
    return Response(res_data)
