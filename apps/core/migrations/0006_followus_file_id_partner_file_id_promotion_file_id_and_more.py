# Generated by Django 5.0.3 on 2024-05-10 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_faq_is_active_faq_is_visible_on_home_page_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='followus',
            name='file_id',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='partner',
            name='file_id',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='promotion',
            name='file_id',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='supportedbrand',
            name='file_id',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='whouareattachment',
            name='file_id',
            field=models.TextField(null=True),
        ),
    ]
