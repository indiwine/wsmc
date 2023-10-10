# Generated by Django 4.2.4 on 2023-09-29 08:49
import logging

from django.apps.registry import Apps
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor

from social_media.common import print_progress_bar
from social_media.geo.geocoderhelper import GeoCoderHelper, GeoCoderSource, GeoCoderQuery
from social_media.models import SmProfile, Country

logger = logging.getLogger(__name__)


def fill_country_names(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    sm_profile: SmProfile = apps.get_model('social_media', 'smprofile')
    country: Country = apps.get_model('social_media', 'country')

    coder = GeoCoderHelper(source=GeoCoderSource.REMOTE)
    count = 0
    total = sm_profile.objects.count()
    if total > 0:
        print_progress_bar(0, total, prefix = 'Progress:', suffix = 'Complete', length = 50)
        for profile in sm_profile.objects.iterator(10000):
            count += 1
            if isinstance(profile.country, str) and len(profile.country) > 0:
                lookup_result = coder.gecode_country(query=GeoCoderQuery(country=profile.country))
                if lookup_result:
                    profile.country_ref, _ = country.objects.get_or_create(code=lookup_result['country_code'], defaults={
                        'name': lookup_result['country'],
                        'code': lookup_result['country_code'],
                    })
                    profile.save()
                else:
                    logger.debug(f'Country "{profile.country}" was not found')
            print_progress_bar(count, total, prefix = 'Progress:', suffix = 'Complete', length = 50)



class Migration(migrations.Migration):
    dependencies = [
        ('social_media', '0031_country_remove_smprofile_social_medi_oid_0920d4_idx_and_more'),
    ]

    operations = [
        migrations.RunPython(fill_country_names),
        # migrations.RemoveField(
        #     model_name='smprofile',
        #     name='country',
        # ),
    ]