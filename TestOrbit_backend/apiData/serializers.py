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
from apiData.models import ApiCaseModule, ApiCase, ApiModule, ApiCaseStep, ApiForeachStep, AssertionRule
from apiData.views.function.viewDef import set_foreach_tree
from utils.comSerializers import ComEditUserNameSerializer
from utils.constant import API_FOREACH, API


class AssertionRuleSerializer(serializers.ModelSerializer):
    """
    断言规则序列化器
    
    用于序列化和反序列化断言规则模型，表示API测试步骤的断言规则。
    """
    class Meta:
        model = AssertionRule
        fields = '__all__'
        
    def to_representation(self, instance):
        """自定义序列化表示"""
        data = super().to_representation(instance)
        # 添加断言的友好显示文本，例如: $.book[0].price == 8.95
        if data['type'] == 'jsonpath':
            expression = data['expression'] 
            operator = data['operator']
            expected = data['expected_value']
            data['display_text'] = f"{expression} {operator} {expected}"
        return data


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
        model = ApiCaseStep
        fields = '__all__'


class ApiCaseStepSerializer(serializers.ModelSerializer):
    """
    API测试用例步骤序列化器
    
    用于序列化ApiCaseStep模型，表示测试用例中的单个步骤。
    特别处理了foreach类型的步骤，通过get_params方法构建步骤的树形结构。
    排除了case、api和quote_case字段，这些关系可能在其他地方处理。
    """
    params = serializers.SerializerMethodField()
    assertions = AssertionRuleSerializer(many=True, read_only=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def to_representation(self, instance):
        # print(f"\n🔄 ApiCaseStepSerializer.to_representation 开始")
        result = super().to_representation(instance)

        # print(f"🔄 ApiCaseStepSerializer.to_representation 结束\n")
        return result

    def get_params(self, obj):
        """
        获取步骤参数，特别处理foreach类型步骤
        
        对于API类型步骤，从关联的ApiCaseStep.params获取参数
        如果步骤是foreach类型，则使用set_foreach_tree函数
        构建并返回嵌套的步骤树结构
        
        Args:
            obj: ApiCaseStep实例
            
        Returns:
            dict: 步骤参数，对于foreach类型会包含steps嵌套结构
        """
        # print("📋 ApiCaseStepSerializer.get_params 开始")
        
        try:
            # 使用新的get_step_params方法获取参数
            params = obj.get_step_params()

        except Exception as e:
            print(f"📋 ❌ 获取步骤参数失败: {e}")
            params = {}
        
        if obj.type == API_FOREACH:
            print("📋 处理 foreach 类型步骤...")
            # 对于foreach类型，添加steps嵌套结构
            params = params.copy() if params else {}
            print("📋 查询 foreach 子步骤...")
            
            try:
                foreach_steps = ApiForeachStep.objects.filter(step_id=obj.id).values().order_by('id')
                print(f"📋 找到 {foreach_steps.count()} 个 foreach 子步骤")
                
                steps_tree = set_foreach_tree(foreach_steps)
                print(f"📋 构建的步骤树: {steps_tree}")
                params['steps'] = steps_tree
            except Exception as e:
                print(f"📋 ❌ 处理 foreach 步骤失败: {e}")
                params['steps'] = []
        
        # print(f"📋 最终参数结果: {params}")
        # print("📋 ApiCaseStepSerializer.get_params 完成")
        return params

    class Meta:
        model = ApiCaseStep
        fields = ('id', 'step_name', 'step_order', 'type', 'status', 'enabled', 
                 'controller_data', 'retried_times', 'results', 'params',
                 'timeout', 'source', 'assertions')


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
        确定步骤是否与指定step_id相关
        
        现在没有api_id了，改为根据step_id来判断关联关系
        
        Args:
            obj: ApiCaseStep实例
            
        Returns:
            bool: 如果是指定的步骤则返回True，否则False
        """
        # print("🔗 ApiCaseRelationApiStepSerializer.get_is_relation 开始")
        
        # 现在使用step_id而不是api_id来判断关联
        target_step_id = self.context.get('step_id')
        if target_step_id:
            target_step_id = int(target_step_id)
            if obj.id == target_step_id:
                return True
        else:
            # 如果没有指定step_id，可能是为了向后兼容，返回False
            print("🔗 ❌ 没有指定step_id")
        
        return False

    def get_params(self, obj):
        """
        获取步骤参数，为foreach类型的步骤添加API关联信息
        
        对于API类型步骤，从关联的ApiData.params获取参数
        对于foreach类型步骤，检查每个子步骤是否使用了指定API，
        并在子步骤中添加is_relation标记
        
        Args:
            obj: ApiCaseStep实例
            
        Returns:
            dict: 步骤参数，对于foreach类型会包含带有is_relation标记的steps结构
        """
        # print("🔗📋 ApiCaseRelationApiStepSerializer.get_params 开始")
        
        try:
            # 使用新的get_step_params方法获取参数
            params = obj.get_step_params()
        except Exception as e:
            print(f"🔗📋 ❌ 获取参数失败: {e}")
            params = {}
        
        if obj.type == API_FOREACH:
            print("🔗📋 处理 foreach 类型...")
            
            foreach_data = list(ApiForeachStep.objects.filter(step_id=obj.id).values().order_by('id'))
            print(f"🔗📋 找到 {len(foreach_data)} 个 foreach 子步骤")
            
            # 现在没有api_id，所以不需要检查API关联，直接构建树结构
            params = params.copy() if params else {}
            params['steps'] = set_foreach_tree(foreach_data)
            print(f"🔗📋 构建的 foreach 树: {params['steps']}")
        
        print(f"🔗📋 最终参数: {params}")
        print("🔗📋 ApiCaseRelationApiStepSerializer.get_params 完成")
        return params

    class Meta:
        model = ApiCaseStep
        fields = ('id', 'step_name', 'step_order', 'type', 'status', 'enabled', 
                 'controller_data', 'retried_times', 'results', 'params', 'is_relation',
                 'timeout', 'source')


class ApiIsRelatedCaseStepMixin:
    """
    处理使用了特定接口的用例步骤查询的混合类
    
    选择合适的步骤序列化器。这使得同一个序列化器可以适应不同的场景。
    """
    @property
    def fields(self):
        """
        动态生成字段，根据上下文选择合适的步骤序列化器

        如果上下文中有step_id，使用ApiCaseRelationApiStepSerializer，
        否则使用ApiCaseStepSerializer。这样可以在需要时显示API关联信息。
        
        Returns:
            dict: 包含动态生成的steps字段的字段字典
        """
        print("\n🔄 ApiIsRelatedCaseStepMixin.fields 属性被访问")
        fields = super().fields
        # 现在改为基于step_id或其他标识来选择序列化器
        step_id = self.context.get('step_id') 
        if step_id:
            fields['steps'] = ApiCaseRelationApiStepSerializer(source='case_step', many=True)
        else:
            fields['steps'] = ApiCaseStepSerializer(source='case_step', many=True)
        
        # print("🔄 ApiIsRelatedCaseStepMixin.fields 属性访问完成")
        return fields


class ApiCaseDetailSerializer(ApiIsRelatedCaseStepMixin, serializers.ModelSerializer):
    """
    API测试用例详情序列化器
    
    用于序列化测试用例的详细信息，包括所有步骤。
    继承自ApiIsRelatedCaseStepMixin，支持显示与特定API的关联信息。
    添加了module_related和only_show等额外信息。
    """
    # 注意：这里的steps字段会被ApiIsRelatedCaseStepMixin动态覆盖
    steps = ApiCaseStepSerializer(source='case_step', many=True)
    module_related = serializers.JSONField(source='module.module_related')
    only_show = serializers.SerializerMethodField()
    
    def __init__(self, *args, **kwargs):
        print("🔧 ApiCaseDetailSerializer.__init__ 开始")
        super().__init__(*args, **kwargs)
    def to_representation(self, instance):
        print(f"\n📤 ApiCaseDetailSerializer.to_representation 开始")
        result = super().to_representation(instance)
        
        return result

    def get_only_show(self, obj):
        """
        确定测试用例是否应该只对创建者显示
        
        根据用例创建者和当前用户的关系，决定是否显示用例
        
        Args:
            obj: ApiCase实例
            
        Returns:
            bool: 如果用户是创建者则返回True，否则False
        """
        # print("👤 ApiCaseDetailSerializer.get_only_show 开始")
        
        result = obj.creater_id == self.context['user_id']

        # print("👤 ApiCaseDetailSerializer.get_only_show 完成")
        return result

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
