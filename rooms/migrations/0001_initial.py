import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('size', models.CharField(choices=[('малое', 'малое'), ('среднее', 'среднее'), ('большое', 'большое')], max_length=20, verbose_name='Размер')),
                ('price_per_night', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Тариф за сутки, руб.')),
            ],
            options={
                'verbose_name': 'Место',
                'verbose_name_plural': 'Места',
                'ordering': ['name'],
                'constraints': [models.CheckConstraint(condition=models.Q(('size__in', ('малое', 'среднее', 'большое'))), name='room_size_valid'), models.CheckConstraint(condition=models.Q(('price_per_night__gt', 0)), name='room_price_positive')],
            },
        ),
    ]
