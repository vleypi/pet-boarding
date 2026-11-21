import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pets', '0001_initial'),
        ('rooms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_in', models.DateField(verbose_name='Дата заезда')),
                ('check_out', models.DateField(verbose_name='Дата выезда')),
                ('is_cancelled', models.BooleanField(default=False, verbose_name='Отменено')),
                ('pet', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bookings', to='pets.pet', verbose_name='Питомец')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bookings', to='rooms.room', verbose_name='Место')),
            ],
            options={
                'verbose_name': 'Бронирование',
                'verbose_name_plural': 'Бронирования',
                'ordering': ['check_in', 'pk'],
                'constraints': [models.CheckConstraint(condition=models.Q(('check_out__gt', models.F('check_in'))), name='booking_check_out_after_check_in')],
            },
        ),
    ]
