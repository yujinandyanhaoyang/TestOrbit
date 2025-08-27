from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.db.models import Value, F
from django.utils import timezone

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from utils.constant import VAR_PARAM, HEADER_PARAM, HOST_PARAM
from utils.views import View
from user.models import ExpendUser, UserCfg, UserTempParams
from user.serializers import UserSerializer

@api_view(['POST'])
@permission_classes((AllowAny,))
def login(request):
    """
    登录接口
    """
    # 验证用户账号密码的内置方法
    user = authenticate(username=request.data['username'], password=request.data['password'])
    if user:
        # # 删除旧的token（如果存在）
        # Token.objects.filter(user_id=user.id).delete()
        # # 创建新的token
        # token = Token.objects.create(user=user)

        # 开发模式下暂时固定token
        if Token.objects.filter(user_id=user.id).exists():
            token = Token.objects.get(user_id=user.id)
        else:
            token = Token.objects.create(user=user)

        user_info = {'username': user.username, 'phone': user.phone}
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        return Response(data={'msg': '登录成功！', 'token': token.key, 'user_info': user_info})  # 返回登录信息及token
    return Response(data={'msg': '密码错误或该账号被禁用！'}, status=status.HTTP_403_FORBIDDEN)


class UserView(View):
    serializer_class = UserSerializer
    queryset = ExpendUser.objects.all().order_by('date_joined')
    filterset_fields = ('is_active',)

    def post(self, request, *args, **kwargs):
        # 如果传递了password字段就用password的字段，没有则默认密码为123456
        pwd = request.data.get('password', '123456')
        request.data['password'] = make_password(pwd)  # 调用内置生成密码方法进行加密
        return self.create(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        admin_user = ExpendUser.objects.get(username='admin')
        if request.data['id'] == admin_user.id:
            if request.data.get('username') and request.data['username'] != 'admin':
                return Response({'msg': '不允许修改admin账号用户名！'}, status=status.HTTP_400_BAD_REQUEST)
            elif 'is_active' in request.data and not request.data['is_active']:
                return Response({'msg': '不能禁用admin账号！'}, status=status.HTTP_400_BAD_REQUEST)
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return Response(data={'msg': "禁止删除用户！"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_user_cfg_params(request):
    """
    获取用户配置和参数
    """
    user_id = request.user.id if request.user else None
    if user_id:
        cfg_data = UserCfg.objects.filter(user_id=user_id).values().first() or {}
        temp_params = []
        queryset = UserTempParams.objects.filter(user_id=user_id).annotate(
            case_name=F('case__name'), param_type_name=F('param_type__name'))
        for param in queryset:
            temp_params.append({key: getattr(param, key) for key in (
                'id', 'type', 'name', 'step_name', 'value', 'case_id', 'case_name', 'param_type_name',
                'param_type_id')})
        params = {key: [] for key in (VAR_PARAM, HEADER_PARAM, HOST_PARAM)}
        for parm in temp_params:
            params[parm['type']].append(parm)
        return Response(data={**cfg_data, 'params': params})
    return Response(data={})


@api_view(['DELETE'])
def clear_user_temp_params(request):
    """
    清除用户的临时参数
    """
    UserTempParams.objects.filter(user_id=request.user.id).delete()
    return Response({'msg': '清除成功！'})


@api_view(['POST'])
def set_user_cfg(request):
    """
    设置用户配置
    """

    UserCfg.objects.update_or_create(user_id=request.user.id, defaults=request.data)
    return Response({'msg': '修改成功！'})


@api_view(['POST'])
def change_password(request):
    """
    用户修改自己的密码
    """
    pwd = make_password(request.data['password'])
    ExpendUser.objects.filter(id=request.user.id).update(password=pwd)
    return Response(data={'msg': '修改成功'})


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def assign_user_projects(request):
    """
    超级管理员分配用户到项目组
    请求参数:
    - user_id: 用户ID
    - project_ids: 项目ID列表 [1, 2, 3]
    """
    try:        
        # 只有超级管理员可以使用此功能
        if not request.user.is_superuser:
            return Response({'msg': '权限不足，只有超级管理员可以分配用户项目'}, 
                           status=status.HTTP_403_FORBIDDEN)
        
        user_id = request.data.get('user_id')
        project_ids = request.data.get('project_ids', [])
        
        # 验证必要参数
        if user_id is None:
            return Response({'msg': '缺少必要参数: user_id'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # 获取用户对象
        try:
            user = ExpendUser.objects.get(id=user_id)
        except ExpendUser.DoesNotExist:
            return Response({'msg': f'用户ID {user_id} 不存在'}, 
                           status=status.HTTP_404_NOT_FOUND)
        
        # 直接设置用户的项目（替换现有关联）
        user.projects.set(project_ids)
        
        # 获取更新后的项目列表
        current_projects = list(user.projects.values('id', 'name'))
        
        return Response({
            'msg': f'成功为用户 {user.username} 分配项目', 
            'user_id': user_id,
            'username': user.username,
            'current_projects': current_projects,
            'project_count': len(current_projects)
        })
        
    except Exception as e:
        return Response({'msg': f'操作失败: {str(e)}'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)
