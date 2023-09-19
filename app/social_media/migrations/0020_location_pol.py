# Generated by Django 4.2.1 on 2023-05-10 08:00

import django.contrib.gis.db.models.fields
from django.apps.registry import Apps
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


# from social_media.models import Location


def move_polygons(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
    location_model = apps.get_model('social_media', 'location')
    for location in location_model.objects.all():
        polygon = GEOSGeometry(location.location_data['geotext'])
        if polygon.geom_type == 'Polygon':
            polygon = MultiPolygon(polygon)

        location.pol = polygon
        location.save()


class Migration(migrations.Migration):

    dependencies = [
        ('social_media', '0019_smprofile_country_smprofile_domain_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='pol',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(default=None, null=True, srid=4326),
        ),
        migrations.RunPython(move_polygons, migrations.RunPython.noop)
    ]
