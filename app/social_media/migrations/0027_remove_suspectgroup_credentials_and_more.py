# Generated by Django 4.2.3 on 2023-07-06 09:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('social_media', '0026_remove_smpost_social_medi_sm_post_cb0c67_idx_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='suspectgroup',
            name='credentials',
        ),
        migrations.RemoveField(
            model_name='suspectgroup',
            name='name',
        ),
        migrations.AddField(
            model_name='smcredential',
            name='in_use',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='smcredential',
            name='last_used_date',
            field=models.DateTimeField(default=None, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='smcredential',
            name='was_last_used',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='smpost',
            name='author_id',
            field=models.PositiveIntegerField(editable=False, verbose_name=''),
        ),
        migrations.AlterField(
            model_name='smpost',
            name='author_type',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='author', to='contenttypes.contenttype'),
        ),
        migrations.AlterField(
            model_name='smpost',
            name='origin_id',
            field=models.PositiveIntegerField(editable=False, verbose_name=''),
        ),
        migrations.AlterField(
            model_name='smpost',
            name='origin_type',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='origin', to='contenttypes.contenttype'),
        ),
        migrations.AlterField(
            model_name='smpost',
            name='screening_status',
            field=models.CharField(choices=[('pe', 'В очікуванні'), ('re', 'Русня'), ('ok', 'Норм')], default='pe', max_length=4),
        ),
        migrations.AlterField(
            model_name='smprofile',
            name='authenticity_status',
            field=models.CharField(choices=[('hn', 'Людина'), ('bt', 'Бот'), ('un', 'Невідомо')], default='un', max_length=4),
        ),
        migrations.AlterField(
            model_name='smprofile',
            name='screening_status',
            field=models.CharField(choices=[('pe', 'В очікуванні'), ('re', 'Русня'), ('ok', 'Норм')], default='pe', max_length=4),
        ),
        migrations.AlterField(
            model_name='suspectgroup',
            name='url',
            field=models.URLField(unique=True),
        ),
    ]
