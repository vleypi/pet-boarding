from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0004_migrate_booking_statuses'),
        ('pets', '0002_help_texts'),
        ('rooms', '0002_help_texts'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='is_cancelled',
        ),
        migrations.AddConstraint(
            model_name='booking',
            constraint=models.CheckConstraint(condition=models.Q(('status__in', ['active', 'cancelled', 'completed'])), name='booking_status_valid'),
        ),
    ]
