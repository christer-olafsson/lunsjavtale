# Generated by Django 5.0.3 on 2024-04-18 07:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scm', '0002_product_title_alter_product_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='photo_url',
        ),
        migrations.AddField(
            model_name='product',
            name='is_adjustable_for_single_staff',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='stock',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name='ProductAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_url', models.TextField()),
                ('is_cover', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='scm.product')),
            ],
            options={
                'db_table': 'lunsjavtale_product_attachments',
                'ordering': ['-id'],
            },
        ),
    ]
