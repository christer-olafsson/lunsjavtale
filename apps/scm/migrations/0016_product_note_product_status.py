# Generated by Django 5.0.3 on 2024-08-13 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scm', '0015_alter_product_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='note',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='approved', max_length=8),
        ),
    ]
