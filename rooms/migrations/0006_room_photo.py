from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0005_room_slug_unique'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='photo',
            field=models.ImageField(blank=True, help_text='JPEG или PNG до 2 МБ', upload_to='rooms/', verbose_name='Фото'),
        ),
    ]
