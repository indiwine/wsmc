from django.contrib.admin import ModelAdmin
from django.contrib import admin
from django.utils.safestring import mark_safe

from social_media.admin.helpers import generate_link_for_model_object, LinkTypes
from social_media.models import SmLikes


class SmLikesAdmin(ModelAdmin):
    actions = None
    list_display_links = None
    ordering = ['id']

    def formatted_owner(self: SmLikes):
        return generate_link_for_model_object(LinkTypes.CHANGE, self.owner, self.owner.name)

    def profile_link(self: SmLikes):
        return mark_safe(f'<a target="_blank" href="{self.owner.id_url()}">{self.owner.id_url()}</a>')

    def post_item(self: SmLikes):
        return generate_link_for_model_object(LinkTypes.CHANGE, self.parent_object, str(self.parent_object))

    def post_permalink(self: SmLikes):
        return mark_safe(f'<a target="_blank" href="{self.parent_object.permalink}">{self.parent_object.permalink}</a>')

    list_display = [formatted_owner, profile_link, post_item, post_permalink]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(SmLikes, SmLikesAdmin)
