from django.contrib import admin

from .blackphraseadmin import BlackPhraseAdmin
from .locationadmin import LocationAdmin
from .screeningreportadmin import ScreeningReportAdmin
from .screeningdetailadmin import ScreeningDetailAdmin
from .smcredentialsadmin import SmCredentialsAdmin
from .smpostsadmin import SmPostsAdmin
from .suspectadmin import SuspectAdmin
from .smprofileadmin import SmProfileAdmin

admin.site.site_header = 'WSMC - Wartime Social Media Crawler'
admin.site.site_title = 'WSMC - Wartime Social Media Crawler'
