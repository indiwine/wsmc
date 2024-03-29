# Generated by Django 4.1.7 on 2023-04-28 07:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_media', '0018_remove_smpost_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='smprofile',
            name='country',
            field=models.CharField(max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='smprofile',
            name='domain',
            field=models.CharField(max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='smprofile',
            name='metadata',
            field=models.JSONField(null=True),
        ),
    ]
