# Generated by Django 5.0.3 on 2024-07-28 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0011_alter_order_status_alter_orderstatus_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderstatus',
            name='note',
            field=models.TextField(blank=True, null=True),
        ),
    ]
