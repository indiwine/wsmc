from django.contrib import admin

from .blackphraseadmin import BlackPhraseAdmin
from .locationadmin import LocationAdmin
from .osintdetailadmin import OsintDetailAdmin
from .osintreportadmin import OsintReportAdmin
from .screeningdetailadmin import ScreeningDetailAdmin
from .screeningreportadmin import ScreeningReportAdmin
from .smcredentialsadmin import SmCredentialsAdmin
from .smlikesadmin import SmLikesAdmin
from .smpostimageadmin import SmPostImageAdmin
from .smpostsadmin import SmPostsAdmin
from .smprofileadmin import SmProfileAdmin
from .smprofilelocationfilteradmin import SmProfileLocationFilterAdmin
from .suspectadmin import SuspectAdmin
from .suspectgroupadmin import SuspectGroupAdmin
from .suspectplaceadmin import SuspectPlaceAdmin

# admin.site.index_template = 'admin/my_index.html'
admin.site.site_header = 'WSMC - Wartime Social Media Crawler'
admin.site.site_title = 'WSMC - Wartime Social Media Crawler'
