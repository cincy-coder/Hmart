# Generated by Django 5.1.4 on 2025-01-20 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart_app', '0018_alter_categoryoffer_discount_percentage_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='discount_amount',
            field=models.IntegerField(),
        ),
    ]
