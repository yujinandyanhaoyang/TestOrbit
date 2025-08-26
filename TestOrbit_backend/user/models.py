from django.contrib.auth.models import AbstractUser
from django.db import models

from utils.constant import VAR_PARAM, WAITING
from project.models import ProjectParamType, Project
from config.models import Environment


class UserProjectRelation(models.Model):
    """用户与项目的关联表"""
    user = models.ForeignKey('ExpendUser', on_delete=models.CASCADE, verbose_name="用户")
    project = models.ForeignKey('project.Project', on_delete=models.CASCADE, verbose_name="项目")
    
    class Meta:
        verbose_name = '用户项目关系'
        db_table = 'user_project_relation'
        unique_together = ('user', 'project')  # 确保用户和项目的组合是唯一的


class ExpendUser(AbstractUser):
    phone = models.CharField(verbose_name="手机号", default='', max_length=255)
    projects = models.ManyToManyField(
        to=Project, 
        through=UserProjectRelation,
        blank=True, 
        verbose_name="关联项目", 
        related_name="users"
    )

    class Meta:
        verbose_name = '用户'
        db_table = 'auth_user'


class UserEditModel(models.Model):
    """
    公共编辑用户来源模型
    """
    creater = models.ForeignKey(to=ExpendUser, on_delete=models.PROTECT, default=1, verbose_name='创建用户')
    updater = models.ForeignKey(to=ExpendUser, related_name="%(class)s_upd_user", on_delete=models.PROTECT,
                                verbose_name='修改用户', null=True)

    class Meta:
        abstract = True


class UserCfg(models.Model):
    user = models.OneToOneField(to=ExpendUser, on_delete=models.CASCADE, primary_key=True, verbose_name="关联用户")
    envir = models.ForeignKey(to=Environment, default=1, on_delete=models.CASCADE, verbose_name="默认用户环境")
    failed_stop = models.BooleanField(default=False, verbose_name="执行失败是否停止（跳过）执行")
    only_failed_log = models.BooleanField(default=False, verbose_name="仅记录失败的日志")
    exec_status = models.SmallIntegerField(default=WAITING, verbose_name='执行状态')

    class Meta:
        verbose_name = '用户配置数据'
        db_table = 'user_cfg'


class UserTempParams(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(to=ExpendUser, on_delete=models.CASCADE, verbose_name="关联用户")
    name = models.CharField(max_length=255, verbose_name="参数名称")
    value = models.JSONField(null=True, verbose_name="参数值")
    case = models.ForeignKey(to='apiData.ApiCase', null=True, on_delete=models.CASCADE, verbose_name="参数来源的用例")
    step_name = models.CharField(max_length=255, verbose_name="参数来源步骤名")  # 步骤id是动态的所以不能直接关联
    type = models.SmallIntegerField(default=VAR_PARAM, verbose_name="请求数据类别（header、var、host）")
    param_type = models.ForeignKey(to=ProjectParamType, default='string', on_delete=models.PROTECT, verbose_name="变量值的类型")

    class Meta:
        verbose_name = '用户临时参数'
        db_table = 'user_temp_params'
