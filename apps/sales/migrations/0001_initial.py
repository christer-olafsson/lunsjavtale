# Generated by Django 5.0.3 on 2024-04-28 12:16

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('scm', '0006_remove_product_discount_percent_remove_product_price_and_more'),
        ('users', '0008_alter_user_phone'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_on', models.DateTimeField(blank=True, null=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('payment_type', models.CharField(choices=[('online', 'Online'), ('pay-by-invoice', 'Pay By Invoice'), ('cash-on-delivery', 'Cash On Delivery')], default='pay-by-invoice', max_length=16)),
                ('delivery_date', models.DateField()),
                ('vat_percent', models.DecimalField(decimal_places=2, default=0, max_digits=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('discount_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('shipping_charge', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('actual_price', models.DecimalField(decimal_places=2, default=0, help_text='price adding vat & discount', max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('final_price', models.DecimalField(decimal_places=2, default=0, help_text='price adding vat & discount', max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='orders', to='users.company')),
                ('coupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='users.usercoupon')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='created_orders', to=settings.AUTH_USER_MODEL)),
                ('shipping_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='users.address')),
            ],
            options={
                'db_table': 'lunsjavtale_orders',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='OrderStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Placed', 'Placed'), ('Confirmed', 'Confirmed'), ('Partially-paid', 'Partially Paid'), ('Payment-completed', 'Payment Completed'), ('Cancelled', 'Cancelled')], default='Placed', max_length=32)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='statuses', to='sales.order')),
            ],
            options={
                'db_table': 'lunsjavtale_order_statuses',
            },
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_on', models.DateTimeField(blank=True, null=True)),
                ('card_holder_name', models.CharField(max_length=128)),
                ('card_number', models.CharField(max_length=128)),
                ('CVV', models.CharField(max_length=6)),
                ('expiry', models.DateField()),
                ('is_default', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='payment_methods', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'lunsjavtale_payment_methods',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='ProductRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('rating', models.PositiveIntegerField(db_index=True, default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('description', models.TextField(null=True)),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='user_ratings', to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='product_ratings', to='scm.product')),
            ],
            options={
                'db_table': 'lunsjavtale_product_ratings',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='SellCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('date', models.DateField()),
                ('quantity', models.PositiveIntegerField(db_index=True, default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('cancelled', models.PositiveIntegerField(default=0)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('price_with_tax', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('added_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_carts', to=settings.AUTH_USER_MODEL)),
                ('added_for', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
                ('invoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='invoice_carts', to='sales.order')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='product_carts', to='scm.product')),
            ],
            options={
                'db_table': 'lunsjavtale_sell_carts',
            },
        ),
        migrations.CreateModel(
            name='UserCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('payment_type', models.CharField(choices=[('online', 'Online'), ('pay-by-invoice', 'Pay By Invoice'), ('cash-on-delivery', 'Cash On Delivery')], default='pay-by-invoice', max_length=16)),
                ('paid_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('added_for', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='cart_items', to=settings.AUTH_USER_MODEL)),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='users', to='sales.sellcart')),
                ('ingredients', models.ManyToManyField(blank=True, to='scm.ingredient')),
            ],
            options={
                'db_table': 'lunsjavtale_user_carts',
            },
        ),
        migrations.CreateModel(
            name='OrderPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('paid_amount', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('payment_info', models.JSONField(blank=True, null=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='created_payments', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='sales.order')),
                ('user_cart', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='sales.usercart')),
            ],
            options={
                'db_table': 'lunsjavtale_order_payments',
            },
        ),
        migrations.CreateModel(
            name='AlterCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('current_cart', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='current_used_carts', to='sales.sellcart')),
                ('previous_cart', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='previous_used_carts', to='sales.sellcart')),
                ('base', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alter_histories', to='sales.usercart')),
            ],
            options={
                'db_table': 'lunsjavtale_alter_carts',
            },
        ),
    ]
