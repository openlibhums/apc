from django.contrib import admin

from plugins.apc.models import *


class SectionAPCAdmin(admin.ModelAdmin):
    list_display = ('section', 'value', 'currency')
    list_filter = ('currency',)


class WaiverApplicationAdmin(admin.ModelAdmin):
    list_display = ('pk', 'article', 'reviewer', 'status')
    raw_id_fields = ('reviewer',)


class ArticleAPCAdmin(admin.ModelAdmin):
    list_display = ('pk', 'article', 'value', 'currency', 'recorded', 'status')
    list_filter = ('status', 'currency')


admin_list = [
    (SectionAPC, SectionAPCAdmin),
    (WaiverApplication, WaiverApplicationAdmin),
    (ArticleAPC, ArticleAPCAdmin),
]

[admin.site.register(*t) for t in admin_list]
