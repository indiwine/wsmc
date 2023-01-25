from django.contrib import admin

from .blackphraseadmin import BlackPhraseAdmin
from .locationadmin import LocationAdmin
from .osintreportadmin import OsintReportAdmin
from .osintdetailadmin import OsintDetailAdmin
from .screeningdetailadmin import ScreeningDetailAdmin
from .screeningreportadmin import ScreeningReportAdmin
from .smcredentialsadmin import SmCredentialsAdmin
from .smpostsadmin import SmPostsAdmin
from .smprofileadmin import SmProfileAdmin
from .suspectadmin import SuspectAdmin


admin.site.index_template = 'admin/my_index.html'
admin.site.site_header = 'WSMC - Wartime Social Media Crawler'
admin.site.site_title = 'WSMC - Wartime Social Media Crawler'
