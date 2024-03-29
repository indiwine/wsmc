from django.contrib import admin

from .blackphraseadmin import BlackPhraseAdmin
from .locationadmin import LocationAdmin
from .osintdetailadmin import OsintDetailAdmin
from .osintreportadmin import OsintReportAdmin
from .screeningdetailadmin import ScreeningDetailAdmin
from .screeningreportadmin import ScreeningReportAdmin
from .smcredentialsadmin import SmCredentialsAdmin
from .smpostimageadmin import SmPostImageAdmin
from .smpostsadmin import SmPostsAdmin
from .smprofileadmin import SmProfileAdmin
from .suspectadmin import SuspectAdmin
from .suspectgroupadmin import SuspectGroupAdmin
from .smlikesadmin import SmLikesAdmin
from .smprofilelocationfilteradmin import SmProfileLocationFilterAdmin

# admin.site.index_template = 'admin/my_index.html'
admin.site.site_header = 'WSMC - Wartime Social Media Crawler'
admin.site.site_title = 'WSMC - Wartime Social Media Crawler'
