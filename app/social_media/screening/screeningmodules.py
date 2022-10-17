from django.db.models import TextChoices


class ScreeningModules(TextChoices):
    POSTS_KEYWORD = 'pk', 'Слова в постах'
