from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0002_help_texts'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='slug',
            field=models.SlugField(blank=True, editable=False, max_length=120, verbose_name='Адрес страницы'),
        ),
    ]
