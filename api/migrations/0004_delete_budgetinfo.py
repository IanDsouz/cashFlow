# Generated by Django 3.2.14 on 2022-08-07 19:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_budgetinfo'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BudgetInfo',
        ),
    ]