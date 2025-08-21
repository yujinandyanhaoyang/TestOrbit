from django.db import models

from utils.comModel import ComTimeModel
# 移除不再使用的导入
# from project.models import Project


class Environment(ComTimeModel):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=32, unique=True, verbose_name="环境名称")
    # 解决技术债务，环境表新增url字段
    url = models.CharField(null=True,max_length=255, verbose_name="环境URL")
    remark = models.TextField(null=True, verbose_name="备注")

    class Meta:
        verbose_name = '环境表'
        db_table = 'environment'

# ProjectEnvirData 模型已移除，因为业务逻辑已改变
# 现在所有项目都可以查看所有环境，不再需要这个关联表
