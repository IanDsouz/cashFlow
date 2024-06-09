# Generated by Django 3.2.14 on 2024-03-04 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0039_alter_savingarea_icon'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='income',
            name='date',
        ),
        migrations.AddField(
            model_name='income',
            name='from_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='income',
            name='to_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]