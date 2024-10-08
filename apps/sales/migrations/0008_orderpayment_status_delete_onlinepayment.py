# Generated by Django 5.0.3 on 2024-06-22 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0007_sellcart_request_status_alter_order_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderpayment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('cancelled', 'Cancelled'), ('completed', 'Completed')], default='pending', max_length=32),
        ),
        migrations.DeleteModel(
            name='OnlinePayment',
        ),
    ]
