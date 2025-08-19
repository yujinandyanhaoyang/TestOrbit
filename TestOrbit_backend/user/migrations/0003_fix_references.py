# Manual migration to fix user model references
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_initial'),
        ('project', '0004_add_projectparamtype'),
    ]

    operations = [
        # Fix UserTempParams.param_type reference
        migrations.AlterField(
            model_name='usertempparams',
            name='param_type',
            field=models.ForeignKey(
                default='string',
                on_delete=django.db.models.deletion.PROTECT,
                to='project.projectparamtype',
                verbose_name='变量值的类型'
            ),
        ),
        
        # Fix UserCfg.envir reference (it should reference project.Project)
        migrations.AlterField(
            model_name='usercfg',
            name='envir',
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to='project.project',
                verbose_name='默认用户环境'
            ),
        ),
    ]
