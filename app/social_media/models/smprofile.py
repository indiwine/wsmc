from typing import Optional

from django.contrib import admin
from django.db.models import Model, ForeignKey, RESTRICT, CASCADE, CharField, DateField, Index

from .smcredential import SmCredential
from .suspect import Suspect
from ..social_media import SocialMediaTypes


class SmProfile(Model):
    credentials = ForeignKey(SmCredential, on_delete=RESTRICT, editable=False)
    suspect = ForeignKey(Suspect, on_delete=CASCADE)

    oid = CharField(max_length=512, null=True, verbose_name='ID', help_text='ID користувача в соціальній мережі')
    name = CharField(max_length=512, verbose_name="Ім'я", help_text="Ім'я як вказано в соціальній мережі")
    university = CharField(max_length=512, null=True, verbose_name='Освіта')
    location = CharField(max_length=512, null=True, verbose_name='Місце проживання')
    home_town = CharField(max_length=512, null=True, verbose_name='Місце народження')
    birthdate = DateField(null=True, verbose_name="Дата народження",
                          help_text='Може бути вказаний поточний рік у випадку якщо рік не вказан в соц мережі')

    def __str__(self):
        return f'{self.suspect.__str__()} у {self.credentials.get_social_media_display()}'

    @admin.display(description='ID URL', empty_value='-')
    def id_url(self) -> Optional[str]:
        if self.oid:
            sm = self.credentials.social_media
            if sm == SocialMediaTypes.FB:
                return f'https://www.facebook.com/profile.php?id={self.oid}'

            if sm == SocialMediaTypes.VK:
                return f'https://vk.com/id{self.oid}'

            if sm == SocialMediaTypes.OK:
                return f'https://ok.ru/profile/{self.oid}'

        return None

    class Meta:
        verbose_name = 'Профіль'
        verbose_name_plural = 'Профілі'
        indexes = [
            Index(fields=['suspect', 'oid'])
        ]
