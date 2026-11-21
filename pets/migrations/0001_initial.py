import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Кличка')),
                ('species', models.CharField(max_length=50, verbose_name='Вид')),
                ('age_months', models.PositiveIntegerField(verbose_name='Возраст, мес.')),
                ('weight_kg', models.FloatField(validators=[django.core.validators.MinValueValidator(0.1)], verbose_name='Вес, кг')),
                ('is_vaccinated', models.BooleanField(default=False, verbose_name='Есть прививки')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='pets', to='users.user', verbose_name='Владелец')),
            ],
            options={
                'verbose_name': 'Питомец',
                'verbose_name_plural': 'Питомцы',
                'ordering': ['name'],
                'constraints': [models.CheckConstraint(condition=models.Q(('weight_kg__gt', 0)), name='pet_weight_positive')],
            },
        ),
    ]
