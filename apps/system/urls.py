#coding=utf-8

from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from views import *

urlpatterns = (
    url(r'^change_password/$',change_password,  {'template_name': 'system/change_password.html'}),
    url(r'^reset_password/$',reset_password,  {'template_name': 'system/reset_password.html'}),

    url(r'^feedback/$',feedback_home,  {'template_name': 'system/feedback.html'}),
    url(r'^feedback/mine/$',feedback_home,  {'template_name': 'system/feedback_mine.html'}),
    url(r'^feedback/data/$',feedback_data),
    url(r'^feedback/mine/data/$',feedback_mine_data),
    url(r'^feedback/save/$',feedback_save),
    url(r'^feedback/reply/$',feedback_reply),
    url(r'^feedback/delete/$',feedback_delete),

    url(r'^log/$',log_home,  {'template_name': 'system/log.html'}),
    url(r'^log/data/$',log_list),

    url(r'^visitor/$',vistor_list,  {'template_name': 'system/visitor.html'}),
    url(r'^visitor/list/data/$',vistor_data),

    url(r'^vcode/$', vcode_list, {'template_name': 'system/vcode.html'}, name='vcode_list'),
    url(r'^vcode/list/data/$', vcode_data, name='vcode_data' ),

    url(r'^version/$',version_list,  {'template_name': 'system/version_list.html'}),
    url(r'^version/list/$',version_list,  {'template_name': 'system/version_list.html'}),
    url(r'^version/list/data/$',version_data),
    url(r'^version/add/$',version_add,  {'template_name': 'system/version_edit.html'}),
    url(r'^version/delete/$',version_delete),
)
