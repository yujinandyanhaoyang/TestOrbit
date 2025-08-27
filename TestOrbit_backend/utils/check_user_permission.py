"""
用户权限检查相关工具函数
提供各种权限检查方法，支持项目级别、模块级别等权限验证
"""
from rest_framework.response import Response


def check_project_permission(user, project_id, operation=None, return_response=False):
    """
    检查用户是否有权限操作指定项目
    
    Args:
        user: 用户对象
        project_id: 项目ID
        operation: 操作名称，用于错误信息，例如"创建"、"删除"等
        return_response: 是否返回Response对象
            - True: 返回(has_permission, response)元组
            - False: 只返回布尔值表示是否有权限
        
    Returns:
        如果return_response=False:
            bool: 是否有权限
        如果return_response=True:
            tuple: (has_permission, response)
                - has_permission: 是否有权限
                - response: 如无权限，返回Response对象；如有权限，返回None
    """
    # 如果是超级管理员，有所有权限
    if user.is_superuser:
        return (True, None) if return_response else True
        
    # 如果不是超级管理员，检查是否与项目有关联
    from user.models import UserProjectRelation
    has_permission = UserProjectRelation.objects.filter(
        user=user,
        project_id=project_id
    ).exists()
    
    # 根据return_response参数决定返回方式
    if not return_response:
        return has_permission
        
    # 返回权限检查结果和响应对象
    if has_permission:
        return True, None
    else:
        operation_msg = f"{operation}此项目" if operation else "操作此项目"
        return False, Response({
            "msg": f"权限不足，您没有权限{operation_msg}",
            "code": 403
        }, status=403)
