from django.conf.urls import url

from plugins.apc import views

urlpatterns = [
    url(r'^$', views.index, name='apc_index'),
    url(r'^waiver/(?P<application_id>\d+)/$', views.waiver_application, name='apc_waiver_application'),
    url(r'^settings/$', views.settings, name='apc_settings'),
]
