from rest_framework import serializers

from user.models import ExpendUser


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    projects = serializers.SerializerMethodField(read_only=True)  # 只读字段，显示用户关联的项目
    project_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True, 
        required=False,
        help_text="项目ID列表，用于分配用户到项目"
    )

    class Meta:
        model = ExpendUser
        fields = '__all__'
    
    def get_projects(self, obj):
        """获取用户关联的项目信息"""
        return [{'id': p.id, 'name': p.name} for p in obj.projects.all()]
