from django.conf import settings
from django.contrib import admin
from django.contrib.admin import ModelAdmin, EmptyFieldListFilter
from django.contrib.postgres.search import SearchQuery
from django.db.models import QuerySet
from django.utils.safestring import mark_safe

from social_media.models import SmPost


class SmPostsAdmin(ModelAdmin):
    search_fields = ['body__search']
    actions = None
    ordering = ['-datetime']

    @admin.display(description='Permalink')
    def permalink(self: SmPost):
        return mark_safe(f'<a href="{self.permalink}" target="_blank">{self.permalink}</a>')

    fields = [permalink, 'social_media', 'datetime', 'body']

    def get_search_results(self, request, queryset: QuerySet, search_term: str):
        result = queryset
        if len(search_term) > 0:
            query = SearchQuery(search_term, config=settings.PG_SEARCH_LANG, search_type='websearch')
            result = queryset.filter(search_vector=query)

        return result, False

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}

        extra_context['show_delete'] = False  # Here
        # extra_context['show_save'] = False
        # extra_context['show_save_and_continue'] = False

        return super().changeform_view(request, object_id, form_url, extra_context)

    def view_link(self: SmPost):
        return mark_safe(f'<a href="{self.permalink}" target="_blank">{self.get_social_media_display()}</a>')

    view_link.short_description = 'Лінк на пост'

    list_display = ('datetime', view_link, 'body')
    list_filter = ('social_media', 'datetime', ('body', EmptyFieldListFilter))

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(SmPost, SmPostsAdmin)
