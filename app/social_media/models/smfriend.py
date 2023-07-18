from django.db.models import Model, ForeignKey, CASCADE, UniqueConstraint, CheckConstraint, Q, F

from .smprofile import SmProfile


class SmFriend(Model):
    profile1 = ForeignKey(SmProfile, on_delete=CASCADE, related_name='profile1')
    profile2 = ForeignKey(SmProfile, on_delete=CASCADE, related_name='profile2')

    class Meta:
        constraints = [
            UniqueConstraint(fields=['profile1', 'profile2'], name='unique_link'),
            CheckConstraint(check=~Q(entity1=F('profile2')), name='no_self_link')
        ]
