# Generated by Django 4.1.7 on 2023-04-27 07:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social_media', '0017_auto_20230427_1051'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='smpost',
            name='profile',
        ),
    ]