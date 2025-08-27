from django.db import models

from utils.comModel import ComTimeModel
from project.models import Project


class Environment(ComTimeModel):
    """
    环境配置模型
    支持全局和局部变量，类似Postman的环境变量管理
    """
    # 环境类型选择
    TYPE_CHOICES = [
        (0, '局部环境'),
        (1, '全局环境'),
    ]
    
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=32, unique=False, verbose_name="环境名称")
    type = models.IntegerField(choices=TYPE_CHOICES, verbose_name="环境类型", help_text="0=局部环境, 1=全局环境")
    
    # 使用JSON字段存储动态变量
    variables = models.JSONField(default=dict, verbose_name="环境变量", help_text="格式: {变量名: {value: 值, description: 描述}}")

    class Meta:
        verbose_name = '环境表'
        db_table = 'environment'
        
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"


# 项目环境关联表，一个项目可以绑定多个环境。一个环境只能绑定一个项目
class ProjectEnvironment(models.Model):
    """
    项目环境关联表
    管理项目与全局环境的关系
    """
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name='project_environments', verbose_name="关联项目")
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE, related_name='project_relations', verbose_name="关联环境")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = '项目环境关系表'
        db_table = 'project_environment'
        unique_together = ('project', 'environment')  # 确保项目和环境的组合是唯一的
        
    def __str__(self):
        return f"{self.project.name} - {self.environment.name}"


# 用例环境关联表，一个用例可以绑定多个环境。一个环境可以绑定多个用例
class CaseEnvironment(models.Model):
    """
    用例环境关联表
    管理API用例与局部环境的关系
    """
    case = models.ForeignKey('apiData.ApiCase', on_delete=models.CASCADE, related_name='case_environments', verbose_name="关联用例")
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE, related_name='case_relations', verbose_name="关联环境")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = '用例环境关系表'
        db_table = 'case_environment'
        unique_together = ('case', 'environment')  # 确保用例和环境的组合是唯一的
        
    def __str__(self):
        return f"{self.case.name} - {self.environment.name}"