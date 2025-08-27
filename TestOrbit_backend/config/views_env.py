from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from config.models import Environment
from utils.check_user_permission import check_project_permission, get_project_id_by_case


def _validate_and_check_permission(user, env_type, project_id, case_id, operation):
    """
    验证参数并检查权限的公共函数
    
    Args:
        user: 用户对象
        env_type: 环境类型
        project_id: 项目ID
        case_id: 用例ID
        operation: 操作名称（用于错误信息）
    
    Returns:
        Response对象或None: 如果验证失败返回错误Response，成功则返回None
    """
    # 验证环境类型
    try:
        env_type = int(env_type) if env_type is not None else None
    except (ValueError, TypeError):
        return Response({
            "msg": "type参数必须是数字类型",
            "code": 400
        }, status=400)
    
    if env_type not in [0, 1]:
        print(f'env_type错误: {env_type}')
        return Response({
            "msg": "type参数必须是0（场景环境）或1（全局环境）",
            "code": 400
        }, status=400)
    
    # 验证必需参数并检查权限
    if env_type == 1:  # 全局环境
        if not project_id:
            return Response({
                "msg": f"{operation}全局环境需要提供project_id参数",
                "code": 400
            }, status=400)
    else:  # 场景环境
        print(f'case_id: {case_id}')
        if not case_id:
            return Response({
                "msg": f"{operation}场景环境需要提供case_id参数",
                "code": 400
            }, status=400)
        project_id = get_project_id_by_case(case_id)
        print(f'从用例获取的project_id: {project_id}')
        if not project_id:
            return Response({'detail': '用例不存在'}, status=404)
    has_permission = check_project_permission(user, project_id)
    
    if not has_permission:
        return Response({'detail': '权限不足'}, status=403)
    
    return None  # 验证通过


@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
def environment_overview(request):
    """
    统一的环境管理接口
    支持全局环境和场景环境的增删改查
    通过type参数区分环境类型：1=全局环境，0=场景环境
    """
    if request.method == 'GET':
        return handle_environment_get(request)
    elif request.method == 'POST':
        return handle_environment_create(request)
    elif request.method == 'PATCH':
        return handle_environment_update(request)
    elif request.method == 'DELETE':
        return handle_environment_delete(request)


def handle_environment_get(request):
    """
    获取环境列表
    全局环境需要project_id，场景环境需要case_id
    """
    env_type = request.query_params.get('type')
    project_id = request.query_params.get('project_id')
    case_id = request.query_params.get('case_id')
    
    # 验证环境类型参数
    try:
        env_type = int(env_type) if env_type else None
    except (ValueError, TypeError):
        return Response({
            "msg": "type参数必须是数字类型",
            "code": 400
        }, status=400)
    
    if env_type not in [0, 1]:
        return Response({
            "msg": "type参数必须是0（场景环境）或1（全局环境）",
            "code": 400
        }, status=400)
    
    # 验证必需参数
    if env_type == 1 and not project_id:  # 全局环境
        return Response({
            "msg": "获取全局环境需要提供project_id参数",
            "code": 400
        }, status=400)
    elif env_type == 0 and not case_id:  # 场景环境
        return Response({
            "msg": "获取场景环境需要提供case_id参数",
            "code": 400
        }, status=400)
    
    try:
        # 根据环境类型构建查询条件
        if env_type == 1:  # 全局环境
            filter_condition = {'type': 1, 'project_relations__project_id': project_id}
        else:  # 场景环境
            filter_condition = {'type': 0, 'case_relations__case_id': case_id}
        
        # 统一查询环境数据
        environments = Environment.objects.filter(**filter_condition).values(
            'id', 'name', 'variables', 'created', 'updated'
        )
        
        # 构造返回数据
        env_data = [
            {
                'id': env['id'],
                'name': env['name'],
                'type': env_type,
                'variables': env['variables'] or {},
                'variable_count': len(env['variables'] or {}),
                'created': env['created'],
                'updated': env['updated']
            }
            for env in environments
        ]
        
        return Response({
            'total_count': len(env_data),
            'data': env_data
        })
        
    except Exception as e:
        env_type_name = "全局" if env_type == 1 else "场景"
        return Response({
            'msg': f'查询{env_type_name}环境失败: {str(e)}',
            'code': 500
        }, status=500)


def handle_environment_create(request):
    """
    创建环境
    全局环境需要project_id，场景环境需要case_id
    """
    env_type = request.data.get('type')
    name = request.data.get('name')
    variables = request.data.get('variables', {})
    project_id = request.data.get('project_id')
    case_id = request.data.get('case_id')
    
    if not name:
        return Response({"msg": "环境名称不能为空", "code": 400}, status=400)
        # 参数验证和权限检查
    validation_result = _validate_and_check_permission(
        request.user, env_type, project_id, case_id, "创建"
    )
    if validation_result:
        return validation_result
    env_type = int(env_type)
    env_type_name = "全局" if env_type == 1 else "场景"
    
    try:
        with transaction.atomic():
            # 创建环境
            environment = Environment.objects.create(
                name=name,
                type=env_type,
                variables=variables
            )
            
            # 创建关联关系
            if env_type == 1:  # 全局环境
                from config.models import ProjectEnvironment
                ProjectEnvironment.objects.create(
                    project_id=project_id,
                    environment=environment
                )
            else:  # 场景环境
                from config.models import CaseEnvironment
                CaseEnvironment.objects.create(
                    case_id=case_id,
                    environment=environment
                )
            
            return Response({
                "msg": f"{env_type_name}环境创建成功",
                "data": {
                    "id": environment.id,
                    "name": environment.name,
                    "type": environment.type
                }
            })
            
    except Exception as e:
        if '1062' in str(e):
            return Response({"msg": "环境名称已存在", "code": 400}, status=400)
        return Response({"msg": f"创建{env_type_name}环境失败: {str(e)}", "code": 500}, status=500)


def handle_environment_update(request):
    """
    更新环境
    """
    env_type = request.data.get('type')
    env_id = request.data.get('id')
    name = request.data.get('name')
    variables = request.data.get('variables')
    project_id = request.data.get('project_id')  # 全局环境需要
    case_id = request.data.get('case_id')        # 场景环境需要
    
    if not env_id:
        return Response({"msg": "环境ID不能为空", "code": 400}, status=400)
    
    # 参数验证和权限检查
    validation_result = _validate_and_check_permission(
        request.user, env_type, project_id, case_id, "更新"
    )
    if validation_result:
        return validation_result
    
    env_type = int(env_type)
    env_type_name = "全局" if env_type == 1 else "场景"
    
    try:
        environment = Environment.objects.get(id=env_id, type=env_type)
        
        # 更新环境信息
        if name:
            environment.name = name
        if variables is not None:
            environment.variables = variables
        environment.save()
        
        return Response({
            "msg": f"{env_type_name}环境更新成功",
            "data": {
                "id": environment.id,
                "name": environment.name,
                "type": environment.type,
                "variables": environment.variables
            }
        })
        
    except Environment.DoesNotExist:
        return Response({"msg": "环境不存在或类型不匹配", "code": 404}, status=404)
    except Exception as e:
        if '1062' in str(e):
            return Response({"msg": "环境名称已存在", "code": 400}, status=400)
        return Response({"msg": f"更新{env_type_name}环境失败: {str(e)}", "code": 500}, status=500)


def handle_environment_delete(request):
    """
    删除环境
    """
    env_type = request.data.get('type')
    env_id = request.data.get('id')
    
    if not env_id:
        return Response({"msg": "环境ID不能为空", "code": 400}, status=400)
    
    try:
        environment = Environment.objects.get(id=env_id, type=env_type)
        env_name = environment.name
        env_type_name = "全局" if environment.type == 1 else "场景"
        
        # 权限检查 - 删除操作需要检查所有关联的权限
        has_permission = request.user.is_superuser
        if not has_permission:
            if environment.type == 1:  # 全局环境
                from config.models import ProjectEnvironment
                project_relations = ProjectEnvironment.objects.filter(environment=environment)
                for relation in project_relations:
                    if check_project_permission(request.user, relation.project_id):
                        has_permission = True
                        break
            else:  # 场景环境
                from config.models import CaseEnvironment
                case_relations = CaseEnvironment.objects.filter(environment=environment)
                for relation in case_relations:
                    project_id = get_project_id_by_case(relation.case_id)
                    if project_id and check_project_permission(request.user, project_id):
                        has_permission = True
                        break
        
        if not has_permission:
            return Response({'detail': '权限不足'}, status=403)
        
        # 删除环境（关联关系会自动删除，因为设置了CASCADE）
        environment.delete()
        
        return Response({
            "msg": f"{env_type_name}环境 '{env_name}' 删除成功"
        })
        
    except Environment.DoesNotExist:
        return Response({"msg": "环境不存在或类型不匹配", "code": 404}, status=404)
    except Exception as e:
        return Response({"msg": f"删除环境失败: {str(e)}", "code": 500}, status=500)
