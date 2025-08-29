
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apiData.models import ApiCaseModule, ApiCase, ApiModule
from apiData.serializers import CaseModuleSerializer, ApiModuleSerializer
from utils.comDef import get_next_id
from utils.treeDef import create_tree, create_cascader_tree
from utils.views import View
from utils.check_user_permission import check_project_permission

"""
存储模块树相关方法
"""

# 展示模块
class CaseModuleViews(View):
    queryset = ApiCaseModule.objects.order_by('created')
    serializer_class = CaseModuleSerializer
    ordering_fields = ('created',)
    
    def post(self, request, *args, **kwargs):
        # 检查权限
        project_id = request.data.get('project_id')
        if not project_id:
            return Response({
                "msg": "缺少必要参数project_id",
                "code": 400
            }, status=400)
            
        has_permission, response = check_project_permission(
            request.user, project_id, operation="在此项目中创建用例模块", return_response=True
        )
        if not has_permission:
            return response
        
        request.data['id'] = get_next_id(ApiCaseModule, 'CaseMod')
        return self.save_related_module(request.data, ApiCaseModule)

    def delete(self, request, *args, **kwargs):
        # 获取要删除的模块
        module_id = request.query_params.get('id') or request.data.get('id')
        if not module_id:
            return Response({
                "msg": "缺少必要参数id",
                "code": 400
            }, status=400)
            
        try:
            module = ApiCaseModule.objects.get(id=module_id)
        except ApiCaseModule.DoesNotExist:
            return Response({
                "msg": "用例模块不存在",
                "code": 404
            }, status=404)
            
        # 检查权限
        has_permission, response = check_project_permission(
            request.user, module.project_id, operation="删除此用例模块", return_response=True
        )
        if not has_permission:
            return response
            
        return self.delete_logically_module(request, ApiCase, *args, **kwargs)
        
    def patch(self, request, *args, **kwargs):
        # 获取要更新的模块
        module_id = request.data.get('id')
        if not module_id:
            return Response({
                "msg": "缺少必要参数id",
                "code": 400
            }, status=400)
            
        try:
            module = ApiCaseModule.objects.get(id=module_id)
        except ApiCaseModule.DoesNotExist:
            return Response({
                "msg": "用例模块不存在",
                "code": 404
            }, status=404)
            
        # 检查权限
        has_permission, response = check_project_permission(
            request.user, module.project_id, operation="修改此用例模块", return_response=True
        )
        if not has_permission:
            return response
            
        return super().patch(request, *args, **kwargs)


    def get(self, request, *args, **kwargs):
        # 通过module_id查询详细信息
        module_id = request.query_params.get('id')
        if not module_id:
            return Response({
                "msg": "缺少必要参数id",
                "code": 400
            }, status=400)
        else:
            # 查询module详情信息
            try:
                module = ApiCaseModule.objects.get(id=module_id)
                return Response({
                    "data":{
                        "module_id":module.id,
                        "name":module.name
                }})
            except ApiCaseModule.DoesNotExist:
                return Response({
                    "msg": "用例模块不存在",
                    "code": 404
                }, status=404)

        



        
# 辅助模块
class ApiModuleViews(View):
    queryset = ApiModule.objects.order_by('created')
    serializer_class = ApiModuleSerializer
    ordering_fields = ('created',)

    def post(self, request, *args, **kwargs):
        request.data['id'] = get_next_id(ApiModule, 'APM')
        return self.save_related_module(request.data, ApiModule)



@api_view(['GET'])
def tree_case_module(request):
    """
    用例模块树
    根据project_id过滤，只返回指定项目下的用例模块
    project_id为必需参数
    """
    project_id = request.query_params.get('project_id')
    if not project_id:
        # 如果没有提供project_id，返回错误信息
        return Response({
            "msg": "缺少必要参数project_id",
            "code": 400
        }, status=400)
    
    # project_id已经在query_params中，create_tree会直接使用
    return Response(data=create_tree(request, ApiCaseModule, ['module_related']))


@api_view(['GET'])
def tree_cascader_module_case(request):
    """
    测试模块带用例的树
    根据project_id过滤，只返回指定项目下的模块及其用例
    project_id为必需参数
    """
    project_id = request.query_params.get('project_id')
    if not project_id:
        # 如果没有提供project_id，返回错误信息
        return Response({
            "msg": "缺少必要参数project_id",
            "code": 400
        }, status=400)
        
    return create_cascader_tree(request, ApiCaseModule, ApiCase, extra_filter={'is_deleted': False})


@api_view(['GET'])
def tree_api_module(request):
    """
    用例模块树
    """
    return Response(data=create_tree(request, ApiModule, ['module_related'], order_fields=['created']))
