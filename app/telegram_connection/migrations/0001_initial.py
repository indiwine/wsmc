# Generated by Django 4.1.2 on 2022-11-02 14:21

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('name', models.CharField(max_length=255, null=True)),
                ('logged_in', models.BooleanField(default=False)),
            ],
        ),
    ]
