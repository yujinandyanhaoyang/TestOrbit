from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0007_delete_projectenvirdata'),
        ('apiData', '0005_alter_apiforeachstep_options_and_more'),
    ]

    operations = [
        # 添加新的 env 字段
        migrations.AddField(
            model_name='apidata',
            name='env',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='config.environment', verbose_name='关联环境'),
        ),
        
        # 添加数据迁移操作 - 从 project_id 复制到 env_id
        migrations.RunSQL(
            sql="UPDATE api_data SET env_id = project_id;",
            reverse_sql="UPDATE api_data SET project_id = env_id;"
        ),
        
        # 删除旧的 project 字段
        migrations.RemoveField(
            model_name='apidata',
            name='project',
        ),
        
        # 添加唯一性约束
        migrations.AlterUniqueTogether(
            name='apidata',
            unique_together={('env', 'path', 'method')},
        ),
    ]
