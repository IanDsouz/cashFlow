# Generated by Django 3.2.14 on 2023-01-28 23:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_alter_expense_expense_reason'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expense',
            name='budget',
        ),
        migrations.AlterField(
            model_name='expense',
            name='expense_reason',
            field=models.CharField(choices=[('Necessary', 'Necessary'), ('Needed', 'Needed'), ('not requred', 'not requred')], default='Necessary', max_length=255),
        ),
    ]
