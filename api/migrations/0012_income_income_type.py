# Generated by Django 3.2.14 on 2023-01-24 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20230124_2318'),
    ]

    operations = [
        migrations.AddField(
            model_name='income',
            name='income_type',
            field=models.CharField(choices=[('Salary', 'Salary'), ('Bonus', 'Bonus'), ('Freelancing', 'Freelancing')], default='Salary', max_length=255),
        ),
    ]
