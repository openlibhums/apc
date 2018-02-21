from django.conf.urls import url

from plugins.apc import views

urlpatterns = [
    url(r'^$', views.index, name='apc_index'),
    url(r'^settings/$', views.settings, name='apc_settings'),
]
