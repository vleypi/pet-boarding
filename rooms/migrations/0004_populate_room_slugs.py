from django.db import migrations
from django.utils.text import slugify
from unidecode import unidecode


def populate_room_slugs(apps, schema_editor):
    """Заполнить slug существующих мест транслитерацией названия и id"""
    Room = apps.get_model("rooms", "Room")
    for room in Room.objects.order_by("pk"):
        base_slug = slugify(unidecode(room.name)) or "room"
        room.slug = f"{base_slug}-{room.pk}"
        room.save(update_fields=["slug"])


class Migration(migrations.Migration):
    """Заполнение адресов страниц мест"""

    dependencies = [
        ("rooms", "0003_room_slug"),
    ]

    operations = [
        migrations.RunPython(populate_room_slugs, migrations.RunPython.noop),
    ]
