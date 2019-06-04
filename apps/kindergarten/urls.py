# coding:utf-8
from django.conf.urls import url
from views import *

urlpatterns = (
    url(r'^subject/$',subject_list,{'template_name': 'kindergarten/subject.html'}),  # 收支科目
    url(r'^icome/$',icome_list,{'template_name': 'kindergarten/icome.html'}),
    url(r'^expense/$',expense_list,{'template_name': 'kindergarten/expense.html'}),  # 支出
    url(r'^subject/data/$',subject_data,),
    url(r'^subject/save/$',subject_save,),
    url(r'^icome/data/$',icome_data, name='icome_data'),  # 收入
    url(r'^icome/save/$',icome_save,),
    url(r'^expense/data/$',expense_data, name='expense_data'),
    url(r'^expense/save/$',expense_save,),

    url(r'^$',kindergarten_list,{'template_name': 'classes/kindergarten.html'}),  # 幼儿园
    url(r'^data/$',kindergarten_data,name='kindergarten_data'),  # 幼儿园列表信息
    url(r'^save/$',kindergarten_save,name='kindergarten_save'),  # 保存

)
