# Generated by Django 5.0.3 on 2024-05-10 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_company_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientdetails',
            name='cover_photo_url_field',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clientdetails',
            name='logo_url_field',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='url_field',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='url_field',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vendor',
            name='url_field',
            field=models.TextField(blank=True, null=True),
        ),
    ]
