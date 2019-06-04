# coding=utf-8

import requests
import traceback
import json

from django.db import models, transaction
from django.conf import settings
from django.utils import timezone

from libs import utils
from apps.account.models import Member
from apps.order.models import Order

class Journals(models.Model):
    RECHARGE = 0
    CONSUME = 1
    DRAWING = 2
    INCOME = 3
    TYPE_CHOICES = (
        (RECHARGE, u'充值'),
        (CONSUME, u'消费'),
        (DRAWING, u'提现'),
        (INCOME, u'收益'),
    )

    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, verbose_name=u"类别")
    total_fee = models.FloatField(verbose_name=u"金额")
    balance = models.FloatField(verbose_name=u"余额")
    description = models.CharField(max_length=200, verbose_name=u"描述")
    notes = models.CharField(max_length=200, verbose_name=u"备注", blank=True, null=True)
    create_user = models.ForeignKey(settings.AUTH_USER_MODEL)
    create_time = models.DateTimeField(verbose_name=u'时间', auto_now_add=True)

    class Meta:
        db_table = "finance_journals"
        verbose_name = u"财务"
        ordering = ('-id',)
        permissions = (
            ("view_journals", u"用户流水"),
            ("view_bill", u"账单记录"),
            ("view_drawing", u"提现记录"),
            ("check_drawing", u"提现状态变更"),
            ("view_promoting", u"推广记录"),
            ("mange_commissionratio", u"分成比例设置"),
        )

    def to_dict(self):
        result = {
            'id': self.id,
            'type': self.type,
            'type_text': self.get_type_display(),
            'total_fee': self.total_fee,
            'balance': self.balance,
            'description': self.description,
            'notes': self.notes,
            'create_user_text': self.create_user.username,
            'create_time': utils.strftime(self.create_time),
        }
        return result


class DrawingAccount(models.Model):
    ALIPAY = 0
    #WEPAY = 1
    BANK = 1
    TYPE_CHOICES = (
        (ALIPAY, u'支付宝'),
        #(WEPAY, u'微信'),
        (BANK, u'银行卡'),
    )

    type = models.PositiveSmallIntegerField(u'类别', choices=TYPE_CHOICES)
    account_number = models.CharField(max_length=100, verbose_name=u"帐号")
    account_name = models.CharField(max_length=100, verbose_name=u"户名")
    account_bank = models.CharField(max_length=100, verbose_name=u"账号银行", null=True, blank=True)
    create_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, editable=False)
    create_time = models.DateTimeField(verbose_name=u'时间', auto_now_add=True)

    class Meta:
        db_table = "finance_drawing_account"
        verbose_name = u"提现账户"

    def __unicode__(self):
        return u'{0},{0},{0},{0}'.format(self.get_type_display(), self.account_name, self.account_number, self.account_bank)

    def to_dict(self):
        result = {
            'id': self.id,
            'type': self.type,
            'account_bank': self.account_bank,
            'type_text': self.get_type_display(),
            'account_number': self.account_number,
            'account_name': self.account_name,
            'create_time': utils.strftime(self.create_time),
            'create_user': self.create_user.id,
            'create_user_text': self.create_user.username,
            'balance': self.create_user.balance,
        }
        return result


class Drawing(models.Model):
    PENDING = 0
    FINISHED = 1
    REJECT = 2
    STATUS_CHOICES = (
        (PENDING, u'提现中'),
        (FINISHED, u'已完成'),
        (REJECT, u'拒绝'),
    )

    no = models.CharField(max_length=20, verbose_name=u"单号", unique=True, error_messages={'unique': u'单号已存在'},
                          editable=False)
    total_fee = models.FloatField(verbose_name=u'金额')
    type = models.PositiveSmallIntegerField(u'提现方式', choices=DrawingAccount.TYPE_CHOICES)
    balance_before = models.FloatField(verbose_name=u'提现前余额', editable=False)
    balance_after = models.FloatField(verbose_name=u'提现后余额', null=True, editable=False)
    account_bank = models.CharField(max_length=100, verbose_name=u"账号银行")
    account_number = models.CharField(max_length=100, verbose_name=u"帐号")
    account_name = models.CharField(max_length=100, verbose_name=u"户名")
    status = models.PositiveSmallIntegerField(u'状态', choices=STATUS_CHOICES, default=PENDING)
    notes = models.CharField(max_length=200, verbose_name=u"备注", blank=True, null=True)
    create_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, editable=False)
    create_time = models.DateTimeField(verbose_name=u'时间', auto_now_add=True)


    def save(self, *args, **kwargs):
        if self.no == None or self.no == '':
            now = timezone.now()
            orders = Drawing.objects.filter(create_time__gte=now.strftime('%Y-%m-%d')).order_by('-no')
            count = orders.count()
            if count == 0:
                self.no = '%s%05d' % (now.strftime('%Y%m%d'), count + 1)
            else:
                self.no = str(int(orders[0].no) + 1)

        super(Drawing, self).save(*args, **kwargs)

    class Meta:
        db_table = "finance_drawing"
        verbose_name = u"提现记录"
        ordering = ('-id',)

    def to_dict(self):
        result = {
            'id': self.id,
            'no': self.no,
            'status': self.status,
            'type':self.type,
            'type_text':self.get_type_display(),
            'balance_before': self.balance_before,
            'balance_after':self.balance_after,
            'status_text': self.get_status_display(),
            'notes':self.notes,
            'total_fee': round(self.total_fee, 2),
            'account_bank': self.account_bank,
            'account_number': self.account_number,
            'account_name': self.account_name,
            'create_time': utils.strftime(self.create_time),
            'create_user_text': self.create_user.username,
            'create_user': self.create_user.name,
            'user_type_text': self.create_user.get_type_display()
        }
        return result


class DrawingStatus(models.Model):
    main = models.ForeignKey(Drawing)
    status = models.PositiveSmallIntegerField(u'状态', choices=Drawing.STATUS_CHOICES)
    create_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    create_time = models.DateTimeField(verbose_name=u'时间', auto_now_add=True)

    class Meta:
        db_table = "finance_drawing_status"
        verbose_name = u"提现记录状态"
        ordering = ('-id',)

    def to_dict(self):
        result = {
            'id': self.id,
            'status': self.status,
            'status_text': self.get_status_display(),
            'create_time': utils.strftime(self.create_time),
            'create_user_text': self.create_user.username
        }
        return result
