# Generated by Django 3.2.14 on 2024-03-04 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0040_auto_20240304_1130'),
    ]

    operations = [
        migrations.AddField(
            model_name='income',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]