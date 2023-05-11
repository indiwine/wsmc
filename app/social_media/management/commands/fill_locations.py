from time import sleep

from django.core.management import BaseCommand

from social_media.models import SmProfile


class Command(BaseCommand):
    help = 'Try to find locations'


    def handle(self, *args, **options):
        for profile in SmProfile.objects.filter(was_collected=True, country='Украина'):
            if profile.identify_location():
                profile.save()



