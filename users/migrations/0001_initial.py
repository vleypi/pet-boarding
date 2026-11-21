from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Имя')),
                ('phone', models.CharField(max_length=30, verbose_name='Телефон')),
                ('role', models.CharField(choices=[('клиент', 'клиент'), ('администратор', 'администратор')], default='клиент', max_length=20, verbose_name='Роль')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
                'ordering': ['name'],
                'constraints': [models.CheckConstraint(condition=models.Q(('role__in', ['клиент', 'администратор'])), name='user_role_valid')],
            },
        ),
    ]
