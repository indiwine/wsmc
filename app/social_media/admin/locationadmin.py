from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.gis.admin import GISModelAdmin

from social_media.models import Location


class LocationAdmin(GISModelAdmin):
    list_display = ['name', 'weight', 'is_valid']
    readonly_fields = ['is_valid']

    # def render_change_form(
    #         self, request, context, add=False, change=False, form_url="", obj: Location = None
    # ):
    #     if change and obj:
    #         dataframe = obj.get_geo_data_frame
    #         if dataframe is not None:
    #             map = dataframe.explore(legend=False)
    #             context['area_map'] = map._repr_html_()
    #
    #     return super().render_change_form(request, context, add, change, form_url, obj)


admin.site.register(Location, LocationAdmin)
