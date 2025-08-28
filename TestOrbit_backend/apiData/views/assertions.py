"""
断言规则相关操作
"""

from django.db import IntegrityError
from django.db.models import F
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apiData.models import ApiCaseStep, AssertionRule
from apiData.serializers import AssertionRuleSerializer
from utils.views import View
import json
import jsonpath


class AssertionRuleView(View):
    """
    断言规则视图
    提供断言规则的CRUD操作
    """
    queryset = AssertionRule.objects.all()
    serializer_class = AssertionRuleSerializer
    filterset_fields = ('step', 'type', 'enabled')
    ordering_fields = ('id',)

    # 获取断言规则列表或详情
    def get(self, request, *args, **kwargs):
        rule_id = request.query_params.get('id')
        step_id = request.query_params.get('step_id')
        
        if rule_id:
            # 获取单个断言规则详情
            rule = AssertionRule.objects.filter(id=rule_id).first()
            if not rule:
                return Response(
                    data={'msg': f'未找到ID为 {rule_id} 的断言规则！'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.serializer_class(rule)
            return Response(data=serializer.data)
        
        if step_id:
            # 获取特定步骤的断言规则
            rules = AssertionRule.objects.filter(step_id=step_id).order_by('id')
            serializer = self.serializer_class(rules, many=True)
            return Response(data=serializer.data)
            
        # 如果没有指定id或step_id，使用父类的list方法
        return self.list(request, *args, **kwargs)

    # 创建或更新断言规则
    def post(self, request, *args, **kwargs):
        data = request.data
        rule_id = data.get('id')
        step_id = data.get('step_id')
        
        # 确保必须提供step_id
        if not step_id and not rule_id:
            return Response(
                data={'msg': '创建断言规则时必须提供step_id！'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 检查步骤是否存在
        step = ApiCaseStep.objects.filter(id=step_id).first()
        if not step and not rule_id:
            return Response(
                data={'msg': f'未找到ID为 {step_id} 的测试步骤！'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        try:
            if rule_id:
                # 更新现有断言规则
                rule = AssertionRule.objects.filter(id=rule_id).first()
                if not rule:
                    return Response(
                        data={'msg': f'未找到ID为 {rule_id} 的断言规则！'}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                serializer = self.serializer_class(rule, data=data, partial=True)
                operation_msg = f'断言规则更新成功！(ID: {rule_id})'
            else:
                # 创建新断言规则
                data['step'] = step_id
                serializer = self.serializer_class(data=data)
                operation_msg = '断言规则创建成功！'
                
            if serializer.is_valid():
                rule = serializer.save()
                operation_msg += f' (断言规则 ID: {rule.id})'
                return Response(
                    data={'msg': operation_msg, 'data': serializer.data}, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    data={'msg': f'数据验证失败: {serializer.errors}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except IntegrityError as e:
            operation_desc = "更新" if rule_id else "创建"
            return Response(
                data={'msg': f'{operation_desc}断言规则时发生数据库约束错误: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            operation_desc = "更新" if rule_id else "创建"
            return Response(
                data={'msg': f'{operation_desc}断言规则时出错: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # 删除断言规则
    def delete(self, request, *args, **kwargs):
        rule_id = request.query_params.get('id')
        if not rule_id:
            return Response(
                data={'msg': '删除断言规则时必须提供id！'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        rule = AssertionRule.objects.filter(id=rule_id).first()
        if not rule:
            return Response(
                data={'msg': f'未找到ID为 {rule_id} 的断言规则！'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        try:
            rule.delete()
            return Response(
                data={'msg': f'断言规则已删除！(ID: {rule_id})'}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                data={'msg': f'删除断言规则时出错: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
def validate_jsonpath(request):
    """
    验证JSONPath表达式
    
    测试JSONPath表达式是否能从JSON数据中提取内容
    """
    data = request.data
    json_data = data.get('json_data', {})
    expression = data.get('expression', '')
    
    if not expression:
        return Response(
            data={'msg': '必须提供JSONPath表达式！'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    try:
        # 确保json_data是字典
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
            
        # 使用jsonpath提取数据
        result = jsonpath.jsonpath(json_data, expression)
        
        if result is False:  # jsonpath在未匹配时返回False
            return Response(
                data={'msg': '表达式未匹配到任何内容', 'valid': False}, 
                status=status.HTTP_200_OK
            )
        
        return Response(
            data={
                'msg': '表达式验证成功', 
                'valid': True, 
                'result': result
            }, 
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            data={'msg': f'验证JSONPath表达式时出错: {str(e)}', 'valid': False}, 
            status=status.HTTP_400_BAD_REQUEST
        )
