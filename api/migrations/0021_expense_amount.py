# Generated by Django 3.2.14 on 2023-01-28 23:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_alter_expense_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]