from django.contrib import admin
from django.contrib.admin import ModelAdmin

from social_media.admin.helpers import generate_link_for_model, LinkTypes
from social_media.models import SmProfile, SmLikes


class SmProfileAdmin(ModelAdmin):

    list_filter = ['was_collected', 'country']

    @admin.display(description='Likes', empty_value='-')
    def get_likes_view_url(self: SmProfile) -> str:
        count = SmLikes.objects.filter(owner_id=self.id).count()
        return generate_link_for_model(LinkTypes.CHANGELIST, SmLikes, f"Likes ({count})", params={"owner_id": self.id})

    readonly_fields = ['id_url', get_likes_view_url]
    list_display = ['name', 'location', 'home_town', 'country', 'university', 'was_collected', get_likes_view_url]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_module_permission(self, request):
        return True


admin.site.register(SmProfile, SmProfileAdmin)
