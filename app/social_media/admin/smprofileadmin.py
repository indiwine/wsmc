from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.contrib.gis.admin import GISModelAdmin
from django.contrib.gis.db.models import Union
from django.db.models import QuerySet, OuterRef, Subquery, Count
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import path
from django.utils.safestring import mark_safe
from import_export.admin import ExportMixin
from import_export.fields import Field
from import_export.resources import ModelResource

from social_media.admin.helpers import generate_link_for_model, LinkTypes, generate_url_for_model
from social_media.models import SmProfile, SmLikes, SmProfileLocationFilter


@admin.action(description="See Likes")
def redirect_to_likes(modeladmin, request, queryset: QuerySet):
    id_list = ",".join(str(item_id) for item_id in queryset.values_list('id', flat=True))
    return redirect(generate_url_for_model(LinkTypes.CHANGELIST, SmLikes, params={'owner_id__in': id_list}))


@admin.action(description="В смітник")
def send_to_junk_action(modeladmin, request, queryset: QuerySet):
    for profile in queryset:
        profile.move_to_junk()


class ProfileLocationPreciseFilter(SimpleListFilter):
    title = 'Location Filter'

    parameter_name = 'location_filter'

    def lookups(self, request, model_admin):
        return [(item.id, str(item)) for item in SmProfileLocationFilter.objects.all()]

    def queryset(self, request, queryset: QuerySet):
        if self.value():
            polygon_subquery = SmProfileLocationFilter.objects.get(id=self.value()).locations.aggregate(Union('pol'))[
                'pol__union']
            return queryset.filter(location_point__intersects=polygon_subquery)


class ProfileLikesCountFilter(SimpleListFilter):
    title = 'Likes Count Filter'
    parameter_name = 'likes_count_filter'

    def lookups(self, request, model_admin):
        return [
            ('1-2', '1-2'),
            ('>=3', '>=3')
        ]

    def queryset(self, request, queryset):
        if self.value() == '1-2':
            return queryset.filter(likes_count__range=(1, 2))
        if self.value() == '>=3':
            return queryset.filter(likes_count__gte=3)

class SmProfileResource(ModelResource):
    like_count = Field()
    permalink = Field()

    class Meta:
        model = SmProfile
        fields = ('id', 'oid', 'name', 'permalink', 'country_ref', 'location', 'like_count')
        export_order = ('id', 'oid', 'name', 'permalink', 'country_ref', 'location', 'like_count')

    def dehydrate_permalink(self, profile: SmProfile):
        return profile.permalink

    def dehydrate_country(self, profile: SmProfile):
        return profile.country_ref.name

    def dehydrate_like_count(self, profile: SmProfile):
        return profile.likes_count


class SmProfileAdmin(ExportMixin, GISModelAdmin):
    list_filter = [
        # 'was_collected',
        # 'location_known',
        # 'location_precise',
        'screening_status',
        'authenticity_status',
        'person_responsible',
        ProfileLocationPreciseFilter,
        ProfileLikesCountFilter,
        'social_media'
    ]
    resource_classes = [SmProfileResource]
    actions = [redirect_to_likes, send_to_junk_action]

    show_full_result_count = False

    @admin.display(description='Likes', empty_value='-', ordering='likes_count')
    def get_likes_view_url(self: SmProfile) -> str:
        count = self.likes_count
        return generate_link_for_model(LinkTypes.CHANGELIST, SmLikes, f"Likes ({count})", params={"owner_id": self.id})

    @admin.display(description='ID URL', empty_value='-')
    def get_id_link(self: SmProfile):
        return mark_safe(f'<a href="{self.id_url()}" target="_blank">{self.id_url()}</a>')

    search_fields = ['oid', 'domain', 'name']
    search_help_text = "Ім'я, ід соц мережі, або домен (наприклад `durov`)"

    readonly_fields = [
        get_id_link,
        get_likes_view_url,
        'oid',
        'name',
        'university',
        'location',
        'home_town',
        'birthdate',
        'domain',
        'metadata',
        'was_collected',
        'suspect_social_media',
        'social_media'
    ]
    list_display = ['name', 'location', 'home_town', 'person_responsible', 'screening_status', 'authenticity_status',
                    get_id_link, get_likes_view_url]

    list_editable = ['person_responsible', 'screening_status', 'authenticity_status']

    def get_queryset(self, request):
        queryset: QuerySet = super().get_queryset(request)
        queryset = queryset.annotate(likes_count=Subquery(
            SmLikes.objects.filter(owner=OuterRef('id')).values('owner').annotate(likes_count=Count('owner')).values(
                'likes_count')[:1]
        ))
        return queryset.filter(in_junk=False)

    def move_to_junk(self, request: HttpRequest, object_id):
        profile = SmProfile.objects.get(id=object_id)
        profile.move_to_junk()
        self.message_user(request, f"Профіль {profile} переміщено в смітник", level=messages.SUCCESS)
        return redirect(generate_url_for_model(LinkTypes.CHANGELIST, SmProfile))

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super().get_urls()
        opts = self.model._meta
        custom_urls = [
            path('<path:object_id>/move-to-junk/', self.move_to_junk,
                 name='%s_%s_move_to_junk' % (opts.app_label, opts.model_name)),
        ]
        return custom_urls + urls


admin.site.register(SmProfile, SmProfileAdmin)
