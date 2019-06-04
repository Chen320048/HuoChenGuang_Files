# coding:utf-8
from django.conf.urls import url

from apps.activity.views import *

urlpatterns = (
    url(r'^list/$',activity_list,{'template_name': 'activity/activity.html'}),  # 活动查看,针对于投资人活动查看
    url(r'^edit/$',activity_edit_list,{'template_name': 'activity/activity_edit.html'}),  # 活动编辑,园长可以编辑活动
    url(r'^data/$',activity_data),  # 活动数据
    url(r'^save/$',activity_save),  # 保存
    # url(r'^control/$',activity_control) # 主动停止活动
)

