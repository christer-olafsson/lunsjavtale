# Generated by Django 5.0.3 on 2024-05-03 13:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_alter_user_phone'),
    ]

    operations = [
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_on', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=256, unique=True)),
                ('email', models.EmailField(max_length=256, null=True, unique=True)),
                ('contact', models.CharField(max_length=15, null=True)),
                ('post_code', models.PositiveIntegerField(blank=True, null=True)),
                ('is_blocked', models.BooleanField(default=False)),
                ('note', models.TextField(blank=True, null=True)),
                ('logo_url', models.TextField(blank=True, null=True)),
                ('formation_date', models.DateField(blank=True, null=True)),
                ('social_media_links', models.JSONField(blank=True, null=True)),
                ('sold_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('withdrawn_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
            ],
            options={
                'db_table': 'lunsjavtale_vendors',
            },
        ),
        migrations.AddField(
            model_name='company',
            name='invoice_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='company',
            name='ordered_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='company',
            name='paid_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AlterField(
            model_name='user',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='users.company'),
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('developer', 'Developer'), ('user', 'User'), ('vendor', 'Vendor'), ('owner', 'Owner'), ('manager', 'Manager'), ('employee', 'Employee')], default='user', max_length=16),
        ),
        migrations.AddField(
            model_name='user',
            name='vendor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='users.vendor'),
        ),
        migrations.CreateModel(
            name='WithdrawRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_on', models.DateTimeField(blank=True, null=True)),
                ('withdraw_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('cancelled', 'Cancelled'), ('completed', 'Completed')], default='pending', max_length=32)),
                ('note', models.TextField(blank=True, null=True)),
                ('vendor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='withdraw_requests', to='users.vendor')),
            ],
            options={
                'db_table': 'lunsjavtale_withdraw_requests',
            },
        ),
    ]
