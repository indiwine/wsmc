from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.gis.admin import GISModelAdmin
from django.db.models import QuerySet, OuterRef, Subquery, Exists, Count

from social_media.admin.helpers import generate_link_for_model, LinkTypes
from social_media.models import SmProfile, SmLikes, SmProfileLocationFilter


class ProfileLocationPreciseFilter(SimpleListFilter):
    title = 'Location Filter'

    parameter_name = 'location_filter'

    def lookups(self, request, model_admin):
        return [(item.id, str(item)) for item in SmProfileLocationFilter.objects.all()]

    def queryset(self, request, queryset: QuerySet):
        if self.value():
            polygon_subquery = SmProfileLocationFilter.objects.get(id=self.value()).locations.filter(
                pol__intersects=OuterRef('location_point'))
            return queryset.filter(Exists(polygon_subquery))


class SmProfileAdmin(GISModelAdmin):
    list_filter = [
        'was_collected',
        'location_known',
        'location_precise',
        ProfileLocationPreciseFilter,
        'country'
    ]

    @admin.display(description='Likes', empty_value='-', ordering='likes_count')
    def get_likes_view_url(self: SmProfile) -> str:
        count = self.likes_count
        return generate_link_for_model(LinkTypes.CHANGELIST, SmLikes, f"Likes ({count})", params={"owner_id": self.id})

    readonly_fields = ['id_url', get_likes_view_url]
    list_display = ['name', 'location', 'home_town', 'country', 'university', 'was_collected', get_likes_view_url]

    def get_queryset(self, request):
        queryset: QuerySet = super().get_queryset(request)
        queryset = queryset.annotate(likes_count=Subquery(
            SmLikes.objects.filter(owner=OuterRef('id')).values('owner').annotate(likes_count=Count('owner')).values(
                'likes_count')[:1]
        ))
        return queryset

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True


admin.site.register(SmProfile, SmProfileAdmin)
