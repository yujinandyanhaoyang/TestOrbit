from django.db import models
from utils.comDef import get_next_id
from utils.comModel import ComTimeModel, ComModuleModel
from utils.constant import WAITING, USER_API
from project.models import Project
from user.models import UserEditModel
from config.models import Environment


class ApiModule(ComTimeModel, ComModuleModel):
    project = models.ForeignKey(to=Project, default=1, verbose_name="关联项目", on_delete=models.CASCADE)

    class Meta:
        verbose_name = '用例模块'
        db_table = 'api_module'

    unique_together = ('project', 'name')

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = get_next_id(ApiModule, 'APM')
        super(ApiModule, self).save(*args, **kwargs)



class ApiCaseModule(ComTimeModel, ComModuleModel):
    name = models.CharField(max_length=100, verbose_name="模块名称")
    position = models.IntegerField(default=0, verbose_name='排序优先级')

    class Meta:
        verbose_name = '用例模块'
        db_table = 'api_case_module'


class ApiCase(ComTimeModel, UserEditModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name="测试用例名称")
    module = models.ForeignKey(to=ApiCaseModule, on_delete=models.PROTECT, verbose_name="所属模块")
    status = models.IntegerField(default=WAITING, verbose_name="执行结果")
    remark = models.TextField(null=True, verbose_name="用例备注")
    report_data = models.JSONField(null=True, verbose_name="测试报告数据")
    is_deleted = models.BooleanField(default=0, verbose_name="是否删除")
    latest_run_time = models.DateTimeField(null=True, verbose_name='最后一次执行时间')
    position = models.IntegerField(default=0, verbose_name='排序优先级')
    env = models.ForeignKey(to=Environment, null=True, blank=True, on_delete=models.PROTECT, verbose_name="引用的环境")

    class Meta:
        verbose_name = '接口用例'
        db_table = 'api_case'
        unique_together = ('name', 'module')
    




class ApiCaseStep(ComTimeModel, models.Model):
    """
    API测试步骤模型
    
    整合了原ApiData的功能，包含所有API信息和测试步骤信息
    成为系统中API管理的核心模型
    """
    # 基础字段
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=50, choices=[
        ('api', 'API'),
        ('sql', 'SQL')
    ], default='api', verbose_name="步骤类型")
    enabled = models.BooleanField(default=True, verbose_name="是否启用")
    # 测试步骤字段
    step_name = models.CharField(max_length=255, null=True, verbose_name="步骤名称")
    step_order = models.PositiveIntegerField(default=1, verbose_name="步骤顺序")
    status = models.IntegerField(default=0, null=True, verbose_name="执行状态")
    retried_times = models.SmallIntegerField(null=True, verbose_name="重试次数")
    controller_data = models.JSONField(null=True, verbose_name="步骤控制器")
    # 参数和测试参数字段
    params = models.JSONField(null=True, verbose_name="详细参数")
    # 结果和配置
    results = models.JSONField(null=True, verbose_name="步骤执行结果")    
    timeout = models.IntegerField(null=True, verbose_name="超时时间")
    source = models.CharField(max_length=50, null=True, verbose_name="API来源") 


    # 关联
    case = models.ForeignKey(to=ApiCase, related_name='case_step', on_delete=models.CASCADE, verbose_name="所属测试用例")
    env = models.ForeignKey(to=Environment, null=True, blank=True, on_delete=models.PROTECT, verbose_name="环境变量")
    # 引用其他用例的外键
    quote_case = models.ForeignKey(to=ApiCase, null=True, blank=True, related_name='quoted_by_steps', 
                                  on_delete=models.PROTECT, verbose_name="引用的用例")

    def get_step_params(self):
        """
        获取步骤参数
        替代原来从ApiData获取params的功能
        
        Returns:
            dict: 步骤的参数字典
        """
        return self.params or {}
    
    def update_step_params(self, new_params):
        """
        更新步骤参数
        替代原来更新ApiData.params的功能
        
        Args:
            new_params (dict): 新的参数字典
            
        Returns:
            bool: 更新是否成功
        """
        self.params = new_params
        self.save(update_fields=['params'])
        return True
        
    def get_api_info(self):
        """
        获取API信息
        替代原来从ApiData获取API详情的功能
        
        Returns:
            dict: API信息字典
        """
        return {
            'name': self.step_name,  # 使用存在的 step_name 字段
            'path': self.params.get('path', '') if self.params else '',  # 从 params 中获取
            'method': self.params.get('method', '') if self.params else '',  # 从 params 中获取
            'timeout': self.timeout,
            'source': self.source,
            'params': self.get_step_params()
        }
    
    class Meta:
        verbose_name = 'api用例的步骤'
        db_table = 'api_case_step'
        unique_together = ('case', 'step_order')


class ApiForeachStep(models.Model):

    step_order = models.PositiveIntegerField(verbose_name="步骤顺序")
    step_name = models.CharField(default='', max_length=255, verbose_name="步骤名称")
    type = models.CharField(default='case', max_length=255,
                            verbose_name="执行参数类型(1.api2.case；3.SQL 4.header（取value） 5.var 6.host)")
    status = models.IntegerField(default=WAITING, verbose_name="执行状态")
    case = models.ForeignKey(null=True, blank=True, to=ApiCase, on_delete=models.PROTECT, verbose_name="关联的用例报告数据")
    enabled = models.BooleanField(default=True, verbose_name="是否启用")
    controller_data = models.JSONField(null=True, verbose_name="步骤控制器")
    quote_case = models.ForeignKey(null=True, to=ApiCase, related_name='%(class)s_quote_case',
                                   on_delete=models.PROTECT, verbose_name="引用的测试用例")
    retried_times = models.SmallIntegerField(null=True, verbose_name="重试了几次")

    step = models.ForeignKey(to=ApiCaseStep, on_delete=models.CASCADE, verbose_name="所属测试步骤")
    parent = models.ForeignKey(null=True, to='self', on_delete=models.CASCADE, verbose_name="父循环步骤")

    class Meta:
        verbose_name = 'api用例循环控制器步骤'
        db_table = 'api_foreach_step'
        # 复合主键：(step, step_order) 确保循环步骤的唯一性
        unique_together = ('step', 'step_order')
