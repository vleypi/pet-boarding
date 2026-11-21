from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0004_populate_room_slugs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='slug',
            field=models.SlugField(editable=False, max_length=120, unique=True, verbose_name='Адрес страницы'),
        ),
    ]
