from django.db import models
from utils.comModel import ConfModel


class Project(ConfModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="名称")

    class Meta:
        verbose_name = '项目配置字典表'
        db_table = 'project'
        ordering = ('position',)


class ProjectParamType(ConfModel):
    id = models.CharField(primary_key=True, max_length=8)

    class Meta:
        verbose_name = '参数类型表'
        db_table = 'project_param_type'
        ordering = ('position',)


class ConfParamType(ConfModel):
    id = models.CharField(primary_key=True, max_length=8)

    class Meta:
        verbose_name = '参数类型表'
        db_table = 'conf_param_type'
        ordering = ('position',)



