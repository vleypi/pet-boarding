import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='price_per_night',
            field=models.PositiveIntegerField(help_text='Целое число рублей больше нуля', validators=[django.core.validators.MinValueValidator(1)], verbose_name='Тариф за сутки, руб.'),
        ),
        migrations.AlterField(
            model_name='room',
            name='size',
            field=models.CharField(choices=[('малое', 'малое'), ('среднее', 'среднее'), ('большое', 'большое')], help_text='Малое до 5 кг, среднее до 20 кг, большое от 20 кг', max_length=20, verbose_name='Размер'),
        ),
    ]
