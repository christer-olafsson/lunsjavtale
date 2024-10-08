# Generated by Django 5.0.3 on 2024-04-28 12:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_coupon_added_for'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=15, null=True, unique=True, validators=[django.core.validators.RegexValidator(message='Enter Valid Phone number with country code', regex='^\\+?1?\\d{9,15}$')], verbose_name='phone number'),
        ),
    ]
