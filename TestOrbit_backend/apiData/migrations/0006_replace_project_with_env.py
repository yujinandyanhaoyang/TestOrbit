from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0007_delete_projectenvirdata'),
        ('apiData', '0005_alter_apiforeachstep_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='apidata',
            old_name='project',
            new_name='env',
        ),
        migrations.AlterField(
            model_name='apidata',
            name='env',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='config.environment', verbose_name='关联环境'),
        ),
        migrations.AlterUniqueTogether(
            name='apidata',
            unique_together={('env', 'path', 'method')},
        ),
        migrations.AlterField(
            model_name='apidata',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='apiData.apimodule', verbose_name='所属模块'),
        ),
    ]
