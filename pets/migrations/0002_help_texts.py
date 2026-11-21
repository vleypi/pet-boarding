import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pets', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pet',
            name='age_months',
            field=models.PositiveIntegerField(help_text='Принимаем питомцев от 3 месяцев', verbose_name='Возраст, мес.'),
        ),
        migrations.AlterField(
            model_name='pet',
            name='species',
            field=models.CharField(help_text='Гостиница принимает кошек и собак', max_length=50, verbose_name='Вид'),
        ),
        migrations.AlterField(
            model_name='pet',
            name='weight_kg',
            field=models.FloatField(help_text='По весу подбирается размер места', validators=[django.core.validators.MinValueValidator(0.1)], verbose_name='Вес, кг'),
        ),
    ]
