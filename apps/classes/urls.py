# coding:utf-8
from django.conf.urls import url

from apps.classes.views import *

urlpatterns = (

    url(r'^grade/$', grade_list,{'template_name': 'classes/grade.html'}),  # 年级
    url(r'^grade/data/$', grade_data,name='grade_data'),  # 年级
    url(r'^grade/save/$', grade_save,name='grade_save'),  # 年级
    # url(r'^class/$', class_list,{'template_name': 'classes/grade.html'}),  # 班级
    url(r'^class/data/$', class_data,name='grade_save'),  # 班级
    url(r'^class/save/$', class_save,name='grade_save'),  # 班级
    url(r'^student/$',student_list,{'template_name': 'classes/student.html'}),  # 学生
    url(r'^student/data/$',student_data, name='student_data'),  # 学生
    url(r'^student/save/$',student_save, name='student_save'),  # 学生
)