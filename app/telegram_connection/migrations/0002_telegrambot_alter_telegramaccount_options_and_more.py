# Generated by Django 4.1.2 on 2022-11-09 08:13

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_connection', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramBot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'Бот',
                'verbose_name_plural': 'Боти',
            },
        ),
        migrations.AlterModelOptions(
            name='telegramaccount',
            options={'verbose_name': 'Обліковий запис Telegram', 'verbose_name_plural': 'Облікові записи Telegram'},
        ),
        migrations.AlterField(
            model_name='telegramaccount',
            name='logged_in',
            field=models.BooleanField(default=False, verbose_name='Логін?'),
        ),
        migrations.AlterField(
            model_name='telegramaccount',
            name='name',
            field=models.CharField(help_text="Ім'я (як записано в Telegram)", max_length=255, null=True, verbose_name="Ім'я"),
        ),
        migrations.AlterField(
            model_name='telegramaccount',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, unique=True, verbose_name='Телефон'),
        ),
        migrations.AddField(
            model_name='telegramaccount',
            name='bots_to_use',
            field=models.ManyToManyField(help_text='Боти що можуть бути використані з цим аккаунтом.', to='telegram_connection.telegrambot', verbose_name='Бот'),
        ),
    ]
