# Generated by Django 4.1.7 on 2023-04-26 14:17

import django.db.models.deletion
from django.apps.registry import Apps
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db import migrations, models

from social_media.models import SmGroup, SmPost, SmProfile







class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('social_media', '0014_remove_smpost_social_medi_sm_post_f3cc3b_idx_and_more'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='smgroup',
            name='social_medi_suspect_920fbf_idx',
        ),
        migrations.RemoveIndex(
            model_name='smpost',
            name='social_medi_sm_post_59156e_idx',
        ),
        migrations.RemoveIndex(
            model_name='smprofile',
            name='social_medi_credent_ca74c7_idx',
        ),
        migrations.AddField(
            model_name='smgroup',
            name='social_media',
            field=models.CharField(choices=[('fb', 'Facebook'), ('vk', 'Вконтакте'), ('ok', 'Однокласники')],
                                   null=True, max_length=4, verbose_name='Соціальна мережа'),
        ),
        migrations.AddField(
            model_name='smpost',
            name='author_id',
            field=models.PositiveIntegerField(null=True, verbose_name=''),
        ),
        migrations.AddField(
            model_name='smpost',
            name='author_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='author',
                                    to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='smprofile',
            name='social_media',
            field=models.CharField(choices=[('fb', 'Facebook'), ('vk', 'Вконтакте'), ('ok', 'Однокласники')],
                                   max_length=4, null=True, verbose_name='Соціальна мережа'),
        ),
        migrations.AddField(
            model_name='vkpoststat',
            name='suspect_group',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE,
                                       to='social_media.suspectgroup'),
        ),
        migrations.AlterField(
            model_name='smpost',
            name='origin_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='origin',
                                    to='contenttypes.contenttype'),
        ),
        migrations.AlterField(
            model_name='vkpoststat',
            name='suspect_social_media',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE,
                                       to='social_media.suspectsocialmediaaccount'),
        ),
        migrations.AlterUniqueTogether(
            name='smgroup',
            unique_together={('oid', 'social_media')},
        ),
        migrations.AlterUniqueTogether(
            name='smpost',
            unique_together={('sm_post_id', 'social_media')},
        ),
        migrations.AlterUniqueTogether(
            name='smprofile',
            unique_together={('oid', 'social_media')},
        ),
        migrations.AddIndex(
            model_name='smgroup',
            index=models.Index(fields=['suspect_group', 'oid', 'credentials', 'social_media'],
                               name='social_medi_suspect_78ef0a_idx'),
        ),
        migrations.AddIndex(
            model_name='smpost',
            index=models.Index(
                fields=['sm_post_id', 'social_media', 'datetime', 'origin_type', 'origin_id', 'author_type',
                        'author_id'], name='social_medi_sm_post_cb0c67_idx'),
        ),
        migrations.AddIndex(
            model_name='smprofile',
            index=models.Index(fields=['credentials', 'oid', 'was_collected', 'suspect_social_media', 'social_media'],
                               name='social_medi_credent_e27885_idx'),
        ),
    ]