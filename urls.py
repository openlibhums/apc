from django.urls import re_path

from plugins.apc import views

urlpatterns = [
    re_path(r'^$', views.index, name='apc_index'),
    re_path(r'^waiver/(?P<application_id>\d+)/$',
        views.waiver_application,
        name='apc_waiver_application',
    ),
    re_path(r'^waiver/new/(?P<article_id>\d+)/$',
        views.make_waiver_application, 
        name='apc_make_waiver_application',
    ),
    re_path(r'^settings/$', views.settings, name='apc_settings'),

    re_path(r'^(?P<apc_id>\d+)/action/(?P<action>paid|unpaid|new|invoiced)/$',
        views.apc_action,
        name='apc_action',
    ),
    re_path(r'^staff/$', views.billing_staff, name='apc_billing_staff'),
    
    re_path(
        r'^staff/new/$', 
        views.manage_billing_staff, 
        name='apc_new_billing_staff',
    ),
    re_path(
        r'^staff/(?P<billing_staffer_id>\d+)/$', 
        views.manage_billing_staff, 
        name='apc_manage_billing_staff',
    ),
    re_path(
        r'^add_article/$',
        views.add_article,
        name='apc_add_article',
    ),
    re_path(r'^discount/(?P<apc_id>\d+)/$',
        views.discount_apc,
        name='discount_apc',
    ),

]
