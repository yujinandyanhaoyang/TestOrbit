from django.db import models
from utils.comModel import ProjectModel


class Project(ProjectModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="名称")
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')

    class Meta:
        verbose_name = '项目配置字典表'
        db_table = 'project'
        ordering = ('position',)
 

class ProjectParamType(ProjectModel):
    id = models.CharField(primary_key=True, max_length=8)
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated = models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')

    class Meta:
        verbose_name = '参数类型表'
        db_table = 'project_param_type'
        ordering = ('position',)




