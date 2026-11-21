from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='check_out',
            field=models.DateField(help_text='Должна быть позже даты заезда', verbose_name='Дата выезда'),
        ),
    ]
