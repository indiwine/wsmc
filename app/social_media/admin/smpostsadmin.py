from django.conf import settings
from django.contrib import admin
from django.contrib.admin import ModelAdmin, EmptyFieldListFilter
from django.contrib.postgres.search import SearchQuery
from django.db.models import QuerySet
from django.forms import ModelForm
from django.utils.safestring import mark_safe

from social_media.models import SmPost


class SmPostAdminFrom(ModelForm):
    class Meta:
        model = SmPost
        exclude = ['raw_post']


class SmPostsAdmin(ModelAdmin):
    form = SmPostAdminFrom
    search_fields = ['body__search']
    actions = []

    def get_search_results(self, request, queryset: QuerySet, search_term: str):
        # result = super().get_search_results(request, queryset, search_term)
        result = queryset
        if len(search_term) > 0:
            query = SearchQuery(search_term, config=settings.PG_SEARCH_LANG)
            result = queryset.filter(search_vector=query)

        return result, False

    def view_link(self):
        return mark_safe(f'<a href="{self.permalink}" target="_blank">{self.get_social_media_display()}</a>')

    view_link.short_description = 'Лінк на пост'

    list_display = ('profile', 'datetime', view_link, 'body')
    list_filter = ('profile', 'social_media', 'datetime', ('body', EmptyFieldListFilter))

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(SmPost, SmPostsAdmin)