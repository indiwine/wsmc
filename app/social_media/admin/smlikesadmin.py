from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.utils.safestring import mark_safe
from import_export.admin import ExportMixin
from import_export.fields import Field
from import_export.resources import ModelResource

from social_media.admin.helpers import generate_link_for_model_object, LinkTypes
from social_media.models import SmLikes


class SmLikesResource(ModelResource):
    permalink = Field()

    class Meta:
        model = SmLikes
        fields = ('owner', 'permalink')
        export_order = ('owner', 'permalink')

    def dehydrate_permalink(self, like: SmLikes):
        return like.parent_object.permalink


class SmLikesAdmin(ExportMixin, ModelAdmin):
    actions = None
    list_display_links = None
    ordering = ['-parent__datetime']
    list_filter = ['parent__datetime', 'parent__screening_status']

    resource_classes = [SmLikesResource]

    def formatted_owner(self: SmLikes):
        return generate_link_for_model_object(LinkTypes.CHANGE, self.owner, self.owner.name)

    def profile_link(self: SmLikes):
        return mark_safe(f'<a target="_blank" href="{self.owner.id_url()}">{self.owner.id_url()}</a>')

    def post_item(self: SmLikes):
        return generate_link_for_model_object(LinkTypes.CHANGE, self.parent_object, str(self.parent_object))

    def post_permalink(self: SmLikes):
        return mark_safe(f'<a target="_blank" href="{self.parent_object.permalink}">{self.parent_object.permalink}</a>')

    @admin.display(ordering='parent__datetime')
    def post_date(self: SmLikes):
        return self.parent_object.datetime

    @admin.display(ordering='parent__screening_status')
    def post_screening_status(self: SmLikes):
        return self.parent_object.get_screening_status_display()

    list_display = [formatted_owner, profile_link, post_item, post_permalink, post_date, post_screening_status]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(SmLikes, SmLikesAdmin)
