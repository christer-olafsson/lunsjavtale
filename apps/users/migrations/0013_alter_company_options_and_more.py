# Generated by Django 5.0.3 on 2024-05-19 07:25

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_partner_logo_url_alter_partner_name_and_more'),
        ('users', '0012_clientdetails_cover_photo_file_id_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='company',
            options={'ordering': ['-created_on'], 'verbose_name_plural': 'Companies'},
        ),
        migrations.RenameField(
            model_name='company',
            old_name='is_contacted',
            new_name='is_checked',
        ),
        migrations.AddField(
            model_name='company',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=32),
        ),
        migrations.AlterField(
            model_name='address',
            name='address_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='addresses', to='core.typeofaddress'),
        ),
        migrations.AlterField(
            model_name='company',
            name='allowance_percentage',
            field=models.PositiveIntegerField(blank=True, default=0, validators=[django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='company',
            name='no_of_employees',
            field=models.PositiveIntegerField(blank=True, default=1),
        ),
    ]
