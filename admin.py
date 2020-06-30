from django.contrib import admin

from plugins.apc.models import *


class SectionAPCAdmin(admin.ModelAdmin):
    list_display = ('section', 'value', 'currency')
    list_filter = ('currency',)
    raw_id_fields = ('section',)


class WaiverApplicationAdmin(admin.ModelAdmin):
    list_display = ('pk', 'article', 'reviewer', 'status')
    raw_id_fields = ('reviewer',)


class ArticleAPCAdmin(admin.ModelAdmin):
    list_display = ('pk', 'article', 'value', 'currency', 'recorded', 'status')
    list_filter = ('status', 'currency')
    raw_id_fields = ('article', 'section_apc')


class BillingStafferAdmin(admin.ModelAdmin):
    list_display = ('pk', 'journal', 'staffer', 'receives_notifications')
    list_filter = ('journal', 'staffer', 'receives_notifications')
    raw_id_fields = ('journal', 'staffer')


class APCDiscountAdmin(admin.ModelAdmin):
    list_display = ('pk', 'amount', 'journal')
    list_display_links = ('pk', 'amount')
    raw_id_fields = ('journal',)
    list_filter = ('journal',)


admin_list = [
    (SectionAPC, SectionAPCAdmin),
    (WaiverApplication, WaiverApplicationAdmin),
    (ArticleAPC, ArticleAPCAdmin),
    (BillingStaffer, BillingStafferAdmin),
    (APCDiscount, APCDiscountAdmin),
]

[admin.site.register(*t) for t in admin_list]
