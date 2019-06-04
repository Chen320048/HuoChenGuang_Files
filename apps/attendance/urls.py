# coding:utf-8
from django.conf.urls import url

from views import *

urlpatterns = (
    url(r'^list/$',attendance_list,{'template_name': 'attendance/attendance.html'}),  # 考勤明细
    url(r'^data/$',attendance_data,name='attendance_data'),  # 考勤明细数据
    url(r'^save/$',attendance_save),  # 保存考勤信息
    url(r'^student/list/$',student_list,{'template_name': 'attendance/student_list.html'}),  # 学生个人考勤汇总
    url(r'^student/attendance/data/$',student_attendance),  # 学生个人考勤汇总数据

    url(r'^refund/list/$',refund_list,{'template_name': 'attendance/refund.html'}),  # 退费
    url(r'^refund/data/$',refund_data,),  # 退费申请表数据
    url(r'^refund/save/$',refund_save,),  # 提交申请
    url(r'^refund/review/list/$',refund_review_list,{'template_name': 'attendance/refund_view.html'}),  # 退费审核列表(园企)
    url(r'^refund/review/$',refund_review_save),  # 对退费申请进行审核


    url(r'^student/data/$',student_data)
)

