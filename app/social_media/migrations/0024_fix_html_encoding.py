# Generated by Django 4.2.1 on 2023-05-17 07:50
import html

from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor



def fix_html_encoding(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    sm_profile_model = apps.get_model('social_media', 'smprofile')
    attrs_to_unescape = ['name', 'university', 'location', 'home_town', 'country']

    for profile in sm_profile_model.objects.all().iterator():
        for attr in attrs_to_unescape:
            current_value = getattr(profile, attr)
            if current_value:
                setattr(profile, attr, html.unescape(current_value))

        profile.save()

class Migration(migrations.Migration):

    dependencies = [
        ('social_media', '0023_remove_smprofile_social_medi_credent_bdf79b_idx_and_more'),
    ]

    operations = [
        migrations.RunPython(fix_html_encoding, reverse_code=migrations.RunPython.noop)
    ]
