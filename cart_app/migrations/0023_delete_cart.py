# Generated by Django 5.1.4 on 2025-02-02 14:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart_app', '0022_cart_delete_cart_model'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Cart',
        ),
    ]
