# Generated by Django 4.1.2 on 2022-12-05 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social_media', '0009_alter_osintdetail_module_alter_suspect_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='smprofile',
            name='oid',
            field=models.CharField(help_text='ID користувача в соціальній мережі', max_length=512, null=True, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='smprofile',
            name='birthdate',
            field=models.DateField(help_text='Може бути вказаний поточний рік у випадку якщо рік не вказан в соц мережі', null=True, verbose_name='Дата народження'),
        ),
        migrations.AlterField(
            model_name='smprofile',
            name='location',
            field=models.CharField(max_length=512, null=True, verbose_name='Місце проживання'),
        ),
        migrations.AlterField(
            model_name='smprofile',
            name='name',
            field=models.CharField(help_text="Ім'я як вказано в соціальній мережі", max_length=512, verbose_name="Ім'я"),
        ),
        migrations.AlterField(
            model_name='smprofile',
            name='university',
            field=models.CharField(max_length=512, null=True, verbose_name='Освіта'),
        ),
        migrations.AddIndex(
            model_name='smprofile',
            index=models.Index(fields=['suspect', 'oid'], name='social_medi_suspect_1292a5_idx'),
        ),
    ]
