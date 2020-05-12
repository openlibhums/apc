from django.conf.urls import url

from plugins.apc import views

urlpatterns = [
    url(r'^$', views.index, name='apc_index'),
    url(r'^waiver/(?P<application_id>\d+)/$',
        views.waiver_application,
        name='apc_waiver_application',
    ),
    url(r'^waiver/new/(?P<article_id>\d+)/$',
        views.make_waiver_application, 
        name='apc_make_waiver_application',
    ),
    url(r'^settings/$', views.settings, name='apc_settings'),

    url(r'^(?P<apc_id>\d+)/action/(?P<action>paid|unpaid|new|invoiced)/$',
        views.apc_action,
        name='apc_action',
    ),
    url(r'^staff/$', views.billing_staff, name='apc_billing_staff'),
    
    url(
        r'^staff/new/$', 
        views.manage_billing_staff, 
        name='apc_new_billing_staff',
    ),
    url(
        r'^staff/(?P<billing_staffer_id>\d+)/$', 
        views.manage_billing_staff, 
        name='apc_manage_billing_staff',
    ),

]
