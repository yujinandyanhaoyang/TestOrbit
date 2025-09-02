"""
测试报告管理相关接口
包括：获取报告列表，查看报告详情，通过id删除报告
"""

import datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

from apiData.models import ApiCase, Report
from project.models import Project
from utils.views import View

# 定义报告分页器
class ReportPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# 报告管理视图类
class ReportViews(View):
    """
    测试报告管理视图类
    提供报告的查询和过滤功能
    """
    queryset = Report.objects.select_related('project', 'creater').order_by('-created')
    pagination_class = ReportPagination
    filterset_fields = ('project',)
    ordering_fields = ('created', 'name')
    diy_search_fields = ('name',)
    
    def get(self, request, *args, **kwargs):
        """
        获取报告列表或详情
        """
        # 如果指定了report_id，则返回详情
        report_id = request.query_params.get('report_id')
        if report_id:
            try:
                # 获取报告详情
                report = Report.objects.get(id=report_id)
                data = {
                    "id": report.id,
                    "name": report.name,
                    "project_id": report.project_id,
                    "project_name": report.project.name if report.project else "未关联项目",
                    "report_data": report.report_data,
                    "created": report.created,
                    "creater_id": report.creater_id,
                    "creater_name": report.creater.username if report.creater else "未知用户",
                }
                return Response(data)
            except Report.DoesNotExist:
                return Response({"message": "报告不存在"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # 返回列表
            return self.list(request, *args, **kwargs)


@api_view(['DELETE'])
def delete_report(request):
    """
    通过id删除报告
    """
    report_id = request.query_params.get('report_id')
    if not report_id:
        return Response({"message": "缺少report_id参数"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        report = Report.objects.get(id=report_id)
        report.delete()
        return Response({"message": "删除成功"})
    except Report.DoesNotExist:
        return Response({"message": "报告不存在"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def batch_delete_reports(request):
    """
    批量删除报告
    """
    report_ids = request.data.get('report_ids', [])
    if not report_ids:
        return Response({"message": "请提供要删除的报告ID列表"}, status=status.HTTP_400_BAD_REQUEST)
    
    deleted_count = Report.objects.filter(id__in=report_ids).delete()[0]
    return Response({"message": f"成功删除{deleted_count}条报告"})


@api_view(['GET'])
def search_reports(request):
    """
    高级搜索报告
    支持按项目名称、报告名称、时间范围等条件过滤
    """
    project_name = request.query_params.get('project_name', '')
    report_name = request.query_params.get('report_name', '')
    start_time = request.query_params.get('start_time', '')
    end_time = request.query_params.get('end_time', '')
    
    # 构建查询条件
    query = Q()
    
    if project_name:
        # 通过project表关联查询
        project_ids = Project.objects.filter(name__icontains=project_name).values_list('id', flat=True)
        query &= Q(project_id__in=project_ids)
    
    if report_name:
        query &= Q(name__icontains=report_name)
    
    if start_time:
        query &= Q(created__gte=start_time)
    
    if end_time:
        query &= Q(created__lte=end_time)
    
    # 执行查询
    reports = Report.objects.filter(query).select_related('project', 'creater').order_by('-created')
    
    # 使用分页
    paginator = ReportPagination()
    paginated_reports = paginator.paginate_queryset(reports, request)
    
    # 构建响应数据
    result = []
    for report in paginated_reports:
        result.append({
            "id": report.id,
            "name": report.name,
            "project_id": report.project_id,
            "project_name": report.project.name if report.project else "未关联项目",
            "report_data": report.report_data,
            "created": report.created,
            "creater_id": report.creater_id,
            "creater_name": report.creater.username if report.creater else "未知用户",
        })
    
    return paginator.get_paginated_response(result)
