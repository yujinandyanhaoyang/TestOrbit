# Manual migration to rename ConfEnvir to Project
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0002_initial'),
    ]

    operations = [
        # Just rename the model in Django's metadata, the table already exists
        migrations.RenameModel(
            old_name='ConfEnvir',
            new_name='Project',
        ),
        
        # Update model options
        migrations.AlterModelOptions(
            name='project',
            options={
                'verbose_name': '项目配置字典表',
                'ordering': ('position',)
            },
        ),
    ]