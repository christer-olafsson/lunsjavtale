# Generated by Django 5.0.3 on 2024-07-12 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_partner_logo_url_alter_partner_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='followus',
            name='title',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
