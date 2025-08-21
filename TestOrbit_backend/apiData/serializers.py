"""
apiData/serializers.py - API 数据序列化器模块

本文件包含与API测试相关的数据序列化器，主要用于处理以下几类数据：
1. API模块 (ApiModule)：API的组织结构
2. API数据 (ApiData)：API接口的具体定义
3. 用例模块 (CaseModule)：测试用例的组织结构
4. 测试用例 (ApiCase)：完整的API测试用例
5. 测试步骤 (ApiCaseStep)：测试用例中的单个步骤
6. 循环步骤 (ApiForeachStep)：支持循环执行的特殊步骤类型

这些序列化器负责在REST API中将模型数据转换为JSON响应，以及将客户端请求转换为模型数据。
序列化器还处理了一些复杂的关联关系，如API与测试用例的关联、循环步骤的树形结构等。
"""

from rest_framework import serializers
from apiData.models import ApiCaseModule, ApiCase, ApiModule, ApiCaseStep, ApiForeachStep, ApiData
from apiData.views.viewDef import set_foreach_tree
from utils.comSerializers import ComEditUserNameSerializer
from utils.constant import API_FOREACH, API


class CaseModuleSerializer(serializers.ModelSerializer):
    """
    测试用例模块序列化器
    
    用于序列化和反序列化ApiCaseModule模型，表示测试用例的组织结构。
    简单序列化器，包含模型的所有字段。
    """
    class Meta:
        model = ApiCaseModule
        fields = '__all__'


class ApiModuleSerializer(serializers.ModelSerializer):
    """
    API模块序列化器
    
    用于序列化和反序列化ApiModule模型，表示API的组织结构。
    简单序列化器，包含模型的所有字段。
    """
    class Meta:
        model = ApiModule
        fields = '__all__'


class ApiDataListSerializer(ComEditUserNameSerializer, serializers.ModelSerializer):
    """
    API数据列表序列化器
    
    用于序列化和反序列化ApiData模型，表示API接口的具体定义。
    继承自ComEditUserNameSerializer，可能添加了创建者和更新者的用户名信息。
    包含模型的所有字段。
    """
    class Meta:
        model = ApiData
        fields = '__all__'


class ApiCaseStepSerializer(serializers.ModelSerializer):
    """
    API测试用例步骤序列化器
    
    用于序列化ApiCaseStep模型，表示测试用例中的单个步骤。
    特别处理了foreach类型的步骤，通过get_params方法构建步骤的树形结构。
    排除了case、api和quote_case字段，这些关系可能在其他地方处理。
    """
    params = serializers.SerializerMethodField()

    def get_params(self, obj):
        """
        获取步骤参数，特别处理foreach类型步骤
        
        如果步骤是foreach类型，则使用set_foreach_tree函数
        构建并返回嵌套的步骤树结构
        
        Args:
            obj: ApiCaseStep实例
            
        Returns:
            dict: 步骤参数，对于foreach类型会包含steps嵌套结构
        """
        if obj.type == API_FOREACH:
            obj.params['steps'] = set_foreach_tree(
                ApiForeachStep.objects.filter(step_id=obj.id).values().order_by('id'))
        return obj.params

    class Meta:
        model = ApiCaseStep
        exclude = ('case', 'api', 'quote_case')


class ApiCaseRelationApiStepSerializer(serializers.ModelSerializer):
    """
    带有API关联信息的测试用例步骤序列化器
    
    扩展了步骤序列化，添加了is_relation字段，表示步骤是否使用了特定API。
    用于在展示API详情时，同时显示使用了该API的测试步骤。
    """
    is_relation = serializers.SerializerMethodField()
    params = serializers.SerializerMethodField()

    def get_is_relation(self, obj):
        """
        确定步骤是否与指定API相关
        
        检查步骤是否直接使用了指定API，或者在foreach步骤中使用了该API
        
        Args:
            obj: ApiCaseStep实例
            
        Returns:
            bool: 如果步骤使用了指定的API则返回True，否则False
        """
        api_id = int(self.context['api_id'])
        if obj.type == API and obj.api_id == api_id:
            return True
        elif obj.type == API_FOREACH:
            foreach_api_ids = list(ApiForeachStep.objects.filter(step_id=obj.id).values_list('api_id', flat=True))
            if api_id in foreach_api_ids:
                return True
        return False

    def get_params(self, obj):
        """
        获取步骤参数，为foreach类型的步骤添加API关联信息
        
        对于foreach类型步骤，检查每个子步骤是否使用了指定API，
        并在子步骤中添加is_relation标记
        
        Args:
            obj: ApiCaseStep实例
            
        Returns:
            dict: 步骤参数，对于foreach类型会包含带有is_relation标记的steps结构
        """
        if obj.type == API_FOREACH:
            api_id = int(self.context['api_id'])
            foreach_data = list(ApiForeachStep.objects.filter(step_id=obj.id).values().order_by('id'))
            for foreach in foreach_data:
                if foreach['api_id'] == api_id:
                    foreach['is_relation'] = True

            obj.params['steps'] = set_foreach_tree(foreach_data)
        return obj.params

    class Meta:
        model = ApiCaseStep
        exclude = ('case', 'api')


class ApiIsRelatedCaseStepMixin:
    """
    处理使用了特定接口的用例步骤查询的混合类
    
    提供了一个动态字段生成方法，根据上下文中是否指定api_id，
    选择合适的步骤序列化器。这使得同一个序列化器可以适应不同的场景。
    """
    @property
    def fields(self):
        """
        动态生成字段，根据上下文选择合适的步骤序列化器
        
        如果上下文中有api_id，使用ApiCaseRelationApiStepSerializer，
        否则使用ApiCaseStepSerializer。这样可以在需要时显示API关联信息。
        
        Returns:
            dict: 包含动态生成的steps字段的字段字典
        """
        fields = super().fields
        fields['steps'] = ApiCaseRelationApiStepSerializer(
            source='case_step', many=True) if self.context['api_id'] else ApiCaseStepSerializer(
            source='case_step', many=True)
        return fields


class ApiCaseDetailSerializer(ApiIsRelatedCaseStepMixin, serializers.ModelSerializer):
    """
    API测试用例详情序列化器
    
    用于序列化测试用例的详细信息，包括所有步骤。
    继承自ApiIsRelatedCaseStepMixin，支持显示与特定API的关联信息。
    添加了module_related和only_show等额外信息。
    """
    steps = ApiCaseStepSerializer(source='case_step', many=True)
    module_related = serializers.JSONField(source='module.module_related')
    only_show = serializers.SerializerMethodField()

    def get_only_show(self, obj):
        """
        确定测试用例是否应该只对创建者显示
        
        根据用例创建者和当前用户的关系，决定是否显示用例
        
        Args:
            obj: ApiCase实例
            
        Returns:
            bool: 如果用户是创建者则返回True，否则False
        """
        return obj.creater_id == self.context['user_id']

    class Meta:
        model = ApiCase
        fields = (
            'id', 'name', 'remark', 'steps', 'module_id', 'latest_run_time', 'updated', 'module_related', 'only_show')


class ApiCaseListSerializer(ComEditUserNameSerializer):
    """
    API测试用例列表序列化器
    
    用于序列化测试用例的简要信息，适用于列表显示。
    继承自ComEditUserNameSerializer，添加了创建者和更新者的用户名信息。
    只包含列表视图所需的基本字段。
    """
    class Meta:
        model = ApiCase
        fields = (
            'id', 'name', 'creater_name', 'latest_run_time', 'updater_name', 'updated', 'created', 'status', 'updater')


class ApiCaseSerializer(ComEditUserNameSerializer):
    """
    API测试用例基本序列化器

    用于序列化和反序列化ApiCase模型的完整信息。
    继承自ComEditUserNameSerializer，添加了创建者和更新者的用户名信息。
    包含模型的所有字段。
    """
    class Meta:
        model = ApiCase
        fields = '__all__'
