from django.contrib import admin

from plugins.apc.models import *


class SectionAPCAdmin(admin.ModelAdmin):
    list_display = ('section_name', 'value', 'currency')
    list_filter = ('currency',)

    def section_name(self, obj):
        return obj.section.name


class WaiverApplicationAdmin(admin.ModelAdmin):
    list_display = ('pk', 'article', 'reviewer', 'status')
    raw_id_fields = ('reviewer',)


class ArticleAPCAdmin(admin.ModelAdmin):
    list_display = ('pk', 'article', 'value', 'currency', 'recorded', 'status')
    list_filter = ('status', 'currency')
    raw_id_fields = ('article', 'section_apc')


admin_list = [
    (SectionAPC, SectionAPCAdmin),
    (WaiverApplication, WaiverApplicationAdmin),
    (ArticleAPC, ArticleAPCAdmin),
]

[admin.site.register(*t) for t in admin_list]
