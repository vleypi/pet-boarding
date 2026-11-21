from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pets', '0002_help_texts'),
    ]

    operations = [
        migrations.AddField(
            model_name='pet',
            name='room_size',
            field=models.GeneratedField(db_persist=True, expression=models.Case(models.When(then=models.Value('малое'), weight_kg__lt=5), models.When(then=models.Value('среднее'), weight_kg__lt=20), default=models.Value('большое')), output_field=models.CharField(max_length=20), verbose_name='Размер места'),
        ),
    ]
