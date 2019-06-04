# coding=utf-8
from django.conf.urls import url

from apps.account.views import *
from apps.account.member_views import *

urlpatterns = (
    # url(r'^administrator/$', account_administrator, {'template_name': 'account/administrator.html'}),  # 网站管理员
    url(r'^investors/$', account_administrator, {'template_name': 'account/investors.html'}),  # 投资人
    url(r'^company/$', account_administrator, {'template_name': 'account/company.html'}),  # 园企
    url(r'^kindergartenor/list/$', kindergartenor_list, {'template_name': 'account/kindergartenor.html'}),  # 幼儿园园长
    url(r'^kindergartenor/data/$', kindergartenor_data),  # 园长数据
    url(r'^kindergartenor/save/$',kindergartenor_save), #  保存园长数据
    url(r'^teacher/list/$',teacher_list,{'template_name': 'account/teacher.html'}),  # 教师
    url(r'^teacher/data/$',teacher_data),  # 教师
    url(r'^teacher/save/$',teacher_save),  # 教师
    url(r'^data/$', account_data),
    url(r'^save/$', account_save),
    url(r'^delete/$', account_delete),

    url(r'^change_password/$', change_password, name='change_password'),
    url(r'change_active/$', change_active, name='account_change_active'),

    url(r'^group/$', group_home, {'template_name': 'account/group.html'}),
    url(r'^group/data/$', group_data),
    url(r'^group/save/$', group_save),
    url(r'^group/delete/$', group_delete),
    url(r'^permission/data/$', permission_data),
    url(r'^class/data/$', class_data),
)

# 会员
# urlpatterns += (
#     url(r'^member/register_via_mobile/$', member_register, {'template_name': 'account/member_register_via_mobile.html'}),
#     url(r'^member/register_via_mobile/save/$', member_register_save, name='member_register_save'),
#     url(r'^member/register_via_mobile/success/$', member_register_success, {'template_name': 'account/member_register_via_mobile_success.html'}),
# )
