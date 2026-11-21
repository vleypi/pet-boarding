from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(help_text='Например, +7 900 111 22 33', max_length=30, verbose_name='Телефон'),
        ),
    ]
