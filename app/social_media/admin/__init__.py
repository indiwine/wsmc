from django.contrib import admin
from .smcredentialsadmin import SmCredentialsAdmin
from .suspectadmin import SuspectAdmin
from .blackphraseadmin import BlackPhraseAdmin

admin.site.site_header = 'WSMC - Wartime Social Media Crawler'
admin.site.site_title = 'WSMC - Wartime Social Media Crawler'