from django.db import migrations, models
import datetime

class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime.now, verbose_name='创建时间'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间'),
        ),
        migrations.AddField(
            model_name='projectparamtype',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime.now, verbose_name='创建时间'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='projectparamtype',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间'),
        ),
    ]
