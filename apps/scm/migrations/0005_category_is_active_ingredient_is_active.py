# Generated by Django 5.0.3 on 2024-04-22 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scm', '0004_remove_product_stock_category_deleted_on_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
