# Generated by Django 5.0.3 on 2024-07-15 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0010_alter_onlinepayment_options_order_is_checked_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Placed', 'Placed'), ('Updated', 'Updated'), ('Partially-paid', 'Partially Paid'), ('Payment-pending', 'Payment Pending'), ('Payment-completed', 'Payment Completed'), ('Cancelled', 'Cancelled'), ('Confirmed', 'Confirmed'), ('Processing', 'Processing'), ('Ready-to-deliver', 'Ready To Deliver'), ('Delivered', 'Delivered')], default='Placed', max_length=32),
        ),
        migrations.AlterField(
            model_name='orderstatus',
            name='status',
            field=models.CharField(choices=[('Placed', 'Placed'), ('Updated', 'Updated'), ('Partially-paid', 'Partially Paid'), ('Payment-pending', 'Payment Pending'), ('Payment-completed', 'Payment Completed'), ('Cancelled', 'Cancelled'), ('Confirmed', 'Confirmed'), ('Processing', 'Processing'), ('Ready-to-deliver', 'Ready To Deliver'), ('Delivered', 'Delivered')], default='Placed', max_length=32),
        ),
    ]
