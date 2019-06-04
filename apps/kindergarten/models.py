# coding:utf-8
from django.db import models
from libs.utils import strftime
from ningmeng import settings
from apps.classes.models import Kindergarten


class Icome(models.Model):
    """收入"""
    notes = models.CharField(max_length=200,null=True,blank=True,verbose_name=u'收入备注')
    balance = models.FloatField(verbose_name=u'收入金额')
    code = models.ForeignKey('Subject',verbose_name=u'科目')
    create_time = models.DateTimeField(auto_now_add=True,editable=False,verbose_name=u'收入时间')
    kindergarten = models.ForeignKey(Kindergarten,on_delete=models.PROTECT, null=True,blank=True,verbose_name=u'幼儿园')
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL,related_name=u'user_icome',on_delete=models.PROTECT,verbose_name=u'提交人')
    class Meta:
        db_table = 'icome'
        verbose_name = u'收入明细管理'
        default_permissions = ()

    def to_dict(self):
        result = {
            'id':self.id,
            'notes':self.notes,
            'balance':self.balance,
            'code':self.code.code,
            'subject': self.code.name,
            'create_time':strftime(self.create_time),
            'submitter':self.submitter.name
        }
        return result


class Expense(models.Model):
    """支出"""
    code = models.ForeignKey('Subject',verbose_name=u'科目')
    balance = models.FloatField(verbose_name=u'支出金额')
    notes = models.CharField(max_length=200,null=True,blank=True,verbose_name=u'支出备注')
    create_time = models.DateTimeField(auto_now_add=True,editable=False,verbose_name=u'支出时间')
    kindergarten = models.ForeignKey(Kindergarten,on_delete=models.PROTECT, null=True,blank=True,verbose_name=u'幼儿园')
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL,related_name=u'user_expense',on_delete=models.PROTECT,verbose_name=u'支出人')
    class Meta:
        db_table = 'expense'
        verbose_name = u'支出明细管理'
        default_permissions = ()

    def to_dict(self):
        result = {
            'id':self.id,
            'notes':self.notes,
            'balance':self.balance,
            'code':self.code.code,
            'subject':self.code.name,
            'create_time':strftime(self.create_time),
            'submitter':self.submitter.name
        }
        return result


class Subject(models.Model):
    """科目"""
    ICOME = 0
    EXPENSE = 1
    STATUS_CHOICES = (
        (ICOME,u'收入',),
        (EXPENSE,u'支出'),
    )

    name = models.CharField(max_length=20,verbose_name=u'科目名称')
    type = models.PositiveSmallIntegerField(choices=STATUS_CHOICES,verbose_name=u'科目类别')
    code = models.CharField(max_length=10,verbose_name=u'科目编码')

    class Meta:
        db_table = 'subject'
        verbose_name = u'科目管理'
        default_permissions = ()

    def to_dict(self):
        result = {
            'id':self.id,
            'name':self.name,
            'type':self.type,
            'type_text':self.get_type_display(),
            'code':self.code
        }
        return result

    def __unicode__(self):
        return self.name



