# Generated by Django 4.1.2 on 2022-11-09 08:13

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('social_media', '0005_alter_screeningreport_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='suspect',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(default=None, max_length=128, null=True, region=None, verbose_name='Телефон'),
        ),
    ]