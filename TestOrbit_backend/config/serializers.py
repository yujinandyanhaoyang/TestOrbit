from rest_framework import serializers

from config.models import Environment, ProjectEnvironment, CaseEnvironment


class EnvironmentVariableSerializer(serializers.Serializer):
    """
    环境变量序列化器
    """
    value = serializers.CharField(max_length=1000, help_text="变量值")
    description = serializers.CharField(max_length=500, required=False, default="", help_text="变量描述")


class EnvironmentSerializer(serializers.ModelSerializer):
    """
    环境序列化器
    """
    variables = serializers.JSONField(required=False, help_text="环境变量配置")
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Environment
        fields = '__all__'
        
    def validate_type(self, value):
        """
        验证环境类型
        """
        if value not in [0, 1]:
            raise serializers.ValidationError("环境类型必须是0（局部环境）或1（全局环境）")
        return value
        
    def validate_variables(self, value):
        """
        验证环境变量格式
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("变量必须是字典格式")
            
        for key, var_config in value.items():
            if not isinstance(var_config, dict):
                raise serializers.ValidationError(f"变量 '{key}' 的配置必须是字典格式")
                
            required_fields = ['value']
            for field in required_fields:
                if field not in var_config:
                    raise serializers.ValidationError(f"变量 '{key}' 缺少必需字段 '{field}'")
                    
        return value


class ProjectEnvironmentSerializer(serializers.ModelSerializer):
    """
    项目环境关系序列化器
    """
    environment_name = serializers.CharField(source='environment.name', read_only=True)
    environment_type = serializers.IntegerField(source='environment.type', read_only=True)
    environment_type_display = serializers.CharField(source='environment.get_type_display', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = ProjectEnvironment
        fields = ['id', 'project', 'environment', 'created_at', 
                 'environment_name', 'environment_type', 'environment_type_display', 'project_name']
        read_only_fields = ['created_at']


class CaseEnvironmentSerializer(serializers.ModelSerializer):
    """
    用例环境关系序列化器
    """
    environment_name = serializers.CharField(source='environment.name', read_only=True)
    environment_type = serializers.IntegerField(source='environment.type', read_only=True)
    environment_type_display = serializers.CharField(source='environment.get_type_display', read_only=True)
    case_name = serializers.CharField(source='case.name', read_only=True)
    
    class Meta:
        model = CaseEnvironment
        fields = ['id', 'case', 'environment', 'created_at',
                 'environment_name', 'environment_type', 'environment_type_display', 'case_name']
        read_only_fields = ['created_at']


class EnvironmentDetailSerializer(serializers.ModelSerializer):
    """
    环境详情序列化器，包含关联的项目信息
    """
    variables = serializers.JSONField(required=False)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    related_projects = serializers.SerializerMethodField()
    variable_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Environment
        fields = ['id', 'name', 'type', 'type_display', 'variables', 
                 'created', 'updated', 'related_projects', 'variable_count']
                 
    def get_related_projects(self, obj):
        """
        获取关联的项目和用例信息
        """
        result = {
            'projects': [],
            'cases': []
        }
        
        # 获取关联的项目信息（全局环境）
        project_relations = obj.project_relations.select_related('project').all()
        result['projects'] = [
            {
                'project_id': relation.project.id,
                'project_name': relation.project.name,
                'created_at': relation.created_at
            }
            for relation in project_relations
        ]
        
        # 获取关联的用例信息（局部环境）
        case_relations = obj.case_relations.select_related('case').all()
        result['cases'] = [
            {
                'case_id': relation.case.id,
                'case_name': relation.case.name,
                'created_at': relation.created_at
            }
            for relation in case_relations
        ]
        
        return result
        
    def get_variable_count(self, obj):
        """
        获取变量数量
        """
        if obj.variables:
            total_count = len(obj.variables)
            return {'total': total_count}
        return {'total': 0}
