# Generated by Django 5.0.3 on 2024-04-02 13:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import apps.bases.utils


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agreement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('data', models.TextField(blank=True)),
                ('type_of', models.CharField(choices=[('terms-and-conditions', 'Term And Conditions'), ('privacy-policy', 'Privacy Policy'), ('instruction-url', 'Instruction Url'), ('about-us', 'About Us')], max_length=20, unique=True)),
            ],
            options={
                'db_table': 'lunsjavtale_agreements',
            },
        ),
        migrations.CreateModel(
            name='PromoCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, unique=True, validators=[apps.bases.utils.coupon_validator])),
                ('promo_type', models.CharField(choices=[('flat', 'flat'), ('percentage', 'percentage')], max_length=100)),
                ('max_uses_limit', models.PositiveIntegerField(default=1)),
                ('max_limit_per_user', models.PositiveIntegerField(default=1)),
                ('value', models.PositiveIntegerField()),
                ('min_amount', models.PositiveIntegerField()),
                ('max_amount', models.PositiveIntegerField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
            ],
            options={
                'db_table': 'lunsjavtale_promo_codes',
            },
        ),
        migrations.AddField(
            model_name='company',
            name='email',
            field=models.EmailField(max_length=256, null=True),
        ),
        migrations.CreateModel(
            name='UserPromoCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('discounted_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_payment_success', models.BooleanField(default=False)),
                ('promo_code', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='users.promocode')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='used_promo_codes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'lunsjavtale_user_promo_codes',
            },
        ),
    ]
