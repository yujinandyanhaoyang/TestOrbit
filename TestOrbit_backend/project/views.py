from functools import lru_cache

from django.db.models import Max
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from utils.paramsDef import get_params_type_func
from utils.views import LimView
from project.models import Project
from project.serializers import ProjectSerializer


class ProjectView(LimView):
    """
    项目视图类
    处理项目的创建、列表、修改和删除
    """
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

    def post(self, request, *args, **kwargs):
        max_id = (Project.objects.aggregate(Max('position')).get('position__max') or 0)
        request.data['position'] = max_id + 1
        
        # 确保处理 creater 字段，由于 Project 不需要这个字段
        if 'creater' in request.data:
            del request.data['creater']
        
        # 创建时间字段由模型自动填充，不需要手动设置
        if 'created' in request.data:
            del request.data['created']
            
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        project_count = Project.objects.count()
        if project_count == 1:
            return Response({'msg': '必须保留至少一个项目！'}, status=status.HTTP_400_BAD_REQUEST)
        return self.destroy(request, *args, **kwargs)


@api_view(['POST'])
def change_project_position(request):
    """
    改变项目的顺序
    """
    project_obj = Project.objects.get(id=request.data['id'])

    if request.data['type'] == 'up':
        new_position = project_obj.position - 1 if project_obj.position > 1 else 1
    else:
        max_id = (Project.objects.aggregate(Max('position')).get('position__max') or 0)
        new_position = project_obj.position + 1 if project_obj.position < max_id else max_id
    Project.objects.filter(position=new_position).update(position=project_obj.position)
    project_obj.position = new_position
    project_obj.save(update_fields=['position'])
    return Response({'msg': '修改成功！'})


@api_view(['GET'])
def get_param_type(request):
    """
    获取参数类型字典
    """
    return Response(data=get_params_type_func())
