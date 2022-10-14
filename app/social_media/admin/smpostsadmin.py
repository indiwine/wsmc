from django.contrib import admin
from django.contrib.admin import ModelAdmin, EmptyFieldListFilter
from django.forms import ModelForm
from django.utils.safestring import mark_safe

from social_media.models import SmPosts


class SmPostAdminFrom(ModelForm):
    class Meta:
        model = SmPosts
        exclude = ['raw_post']


class SmPostsAdmin(ModelAdmin):
    form = SmPostAdminFrom

    def view_link(self):
        return mark_safe(f'<a href="{self.permalink}" target="_blank">{self.get_social_media_display()}</a>')

    view_link.short_description = 'Лінк на пост'

    list_display = ('profile', 'datetime', view_link, 'body')
    list_filter = ('profile', 'social_media', 'datetime', ('body', EmptyFieldListFilter))

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(SmPosts, SmPostsAdmin)
