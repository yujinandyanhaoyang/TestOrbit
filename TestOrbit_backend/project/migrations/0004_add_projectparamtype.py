# Manual migration to add missing ProjectParamType model
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0003_rename_confenvir_project'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectParamType',
            fields=[
                ('name', models.CharField(max_length=100, verbose_name='名称')),
                ('position', models.SmallIntegerField(default=1, verbose_name='排序')),
                ('id', models.CharField(max_length=8, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': '参数类型表',
                'db_table': 'project_param_type',
                'ordering': ('position',),
            },
        ),
    ]
