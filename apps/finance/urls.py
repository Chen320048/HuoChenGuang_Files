# coding=utf-8

from django.conf.urls import url

from apps.finance.views import *

urlpatterns = (
    # 财务流水
    url(r'^journal/$', journal, {'template_name': 'finance/journal.html'}),
    url(r'^journal/data/$', journal_data),

    # 账单
    url(r'^bill/$', bill, {'template_name': 'finance/bill.html'}),
    url(r'^bill/data/$', bill_data),

    # 推广记录
    url(r'^promoting/$', promoting, {'template_name': 'finance/promoting.html'}),
    url(r'^promoting/data/$', promoting_data),

    # 收益记录
    url(r'^income/$', income, {'template_name': 'finance/income.html'}),
    url(r'^income/data/$', income_data),

    # 提现账户
    url(r'^drawing/account/$', drawing_account, {'template_name': 'finance/drawing_account.html'}),
    url(r'^drawing/account/data/$', drawing_account_data),
    url(r'^drawing/account/save/$', drawing_account_save),
    url(r'^drawing/account/delete/$', drawing_account_delete),

    # 提现记录
    url(r'^drawing/record/$', drawing_record, {'template_name': 'finance/drawing_record.html'}),
    url(r'^drawing/record/data/$', drawing_record_data),
    url(r'^drawing/record/accept/$', drawing_record_accept),  # 提现受理/拒绝

    # 提现申请
    url(r'^drawing/$', drawing_withdraw, {'template_name': 'finance/drawing.html'}),  # 提现申请

    url(r'^commission_ratio/$', commission_ratio_home, {'template_name': 'finance/commission_ratio.html'}),
    url(r'^commission_ratio/data/$', commission_ratio_list),
    url(r'^commission_ratio/save/$', commission_ratio_save),
    url(r'^commission_ratio/delete/$', commission_ratio_delete),

)
