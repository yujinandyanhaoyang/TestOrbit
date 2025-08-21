from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0006_remove_foreign_key'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProjectEnvirData',
        ),
    ]
