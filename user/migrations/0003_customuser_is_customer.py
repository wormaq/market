# Generated by Django 4.2 on 2023-05-03 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_remove_customuser_is_stuff_customer_post_code_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='is_customer',
            field=models.BooleanField(default=False),
        ),
    ]
