# Generated by Django 4.1.2 on 2022-11-11 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_media', '0007_alter_screeningreport_options_alter_suspect_phone_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='suspect',
            name='email',
            field=models.EmailField(blank=True, default=None, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='suspect',
            name='name',
            field=models.CharField(max_length=255, verbose_name='ФІО'),
        ),
    ]
