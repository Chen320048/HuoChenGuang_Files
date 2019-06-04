#coding=utf-8

from django.conf.urls import url

from apps.dashboard.views import *

urlpatterns = (
    url(r'^login/$', login),
    url(r'^home/$', home, {'template_name': 'dashboard/home.html'}),
)