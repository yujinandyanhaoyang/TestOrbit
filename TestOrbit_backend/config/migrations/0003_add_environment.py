# Manual migration to add Environment model  
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0002_initial'),
        ('project', '0004_add_projectparamtype'),
    ]

    operations = [
        migrations.CreateModel(
            name='Environment',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')),
                ('id', models.SmallAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='环境名称')),
                ('remark', models.TextField(null=True, verbose_name='备注')),
            ],
            options={
                'verbose_name': '环境表',
                'db_table': 'environment',
            },
        ),
        
        # Update ProjectEnvirData to use correct references
        migrations.AlterField(
            model_name='projectenvirdata',
            name='envir',
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='pro_data_envir',
                to='config.environment',
                verbose_name='关联环境',
            ),
        ),
        migrations.AlterField(
            model_name='projectenvirdata',
            name='project',
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to='project.project',
                verbose_name='关联项目',
            ),
        ),
    ]
