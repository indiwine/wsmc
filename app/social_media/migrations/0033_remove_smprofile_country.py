# Generated by Django 4.2.4 on 2023-09-29 20:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social_media', '0032_remove_country_field'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='smprofile',
            name='country',
        ),
    ]
