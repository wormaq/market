# Generated by Django 4.2 on 2023-05-03 14:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0011_comment_product_alter_comment_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='product',
        ),
    ]