# Generated by Django 5.0.3 on 2024-05-19 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_followus_file_id_partner_file_id_promotion_file_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partner',
            name='logo_url',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='partner',
            name='name',
            field=models.CharField(max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='supportedbrand',
            name='logo_url',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='supportedbrand',
            name='name',
            field=models.CharField(max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='validarea',
            name='post_code',
            field=models.PositiveIntegerField(unique=True),
        ),
    ]
