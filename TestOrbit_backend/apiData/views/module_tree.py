
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apiData.models import ApiCaseModule, ApiCase, ApiModule
from apiData.serializers import CaseModuleSerializer, ApiModuleSerializer
from utils.comDef import get_next_id
from utils.treeDef import create_tree, create_cascader_tree
from utils.views import View

"""
存储模块树相关方法
"""

# 展示模块
class CaseModuleViews(View):
    queryset = ApiCaseModule.objects.order_by('created')
    serializer_class = CaseModuleSerializer
    ordering_fields = ('created',)

    def post(self, request, *args, **kwargs):
        request.data['id'] = get_next_id(ApiCaseModule, 'ACM')
        return self.save_related_module(request.data, ApiCaseModule)

    def delete(self, request, *args, **kwargs):
        return self.delete_logically_module(request, ApiCase, *args, **kwargs)

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
    """
    return Response(data=create_tree(request, ApiCaseModule, ['module_related']))


@api_view(['GET'])
def tree_cascader_module_case(request):
    """
    测试模块带用例的树
    """
    return create_cascader_tree(request, ApiCaseModule, ApiCase, extra_filter={'is_deleted': False})


@api_view(['GET'])
def tree_api_module(request):
    """
    用例模块树
    """
    return Response(data=create_tree(request, ApiModule, ['module_related'], order_fields=['created']))
