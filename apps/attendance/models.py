# coding:utf-8
from django.db import models

from apps.classes.models import Classes,Student
from libs.utils import strftime,strfdate
from ningmeng import settings


class Attendance(models.Model):
    NORMAL = 0
    ABSENCE = 1
    STATUS_CHOICES = (
        (NORMAL,u'正常'),
        (ABSENCE,u'缺勤')
    )
    student = models.ForeignKey(Student,on_delete=models.PROTECT,editable=False,verbose_name=u'学生')
    classes = models.ForeignKey(Classes,on_delete=models.PROTECT,null=True,blank=True,verbose_name=u'班级')
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES,default=NORMAL,verbose_name=u'考勤')
    date = models.DateField(auto_now_add=True,null=True,blank=True,verbose_name=u'考勤日期')
    start_time = models.DateTimeField(auto_now_add=True,null=True,blank=True,verbose_name=u'填报时间')
    notes = models.CharField(max_length=200,null=True,blank=True,verbose_name=u'备注')
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True,verbose_name=u'填报人')

    class Meta:
        db_table = 'attendance'
        verbose_name = u'考勤'
        default_permissions = ()

    def to_dict(self):
        result = {
            'id':self.id,
            'student':self.student.name,
            'class':self.classes.name,
            'grade':self.classes.grade.name,
            'status':self.status,
            # 'status_text':self.get_status_display(),
            'start_time':strfdate(self.date),
            'notes':self.notes,
            'submitter':self.submitter.name
        }
        return result


class Absence(models.Model):
    REVIEW = 0
    FINISH = 1
    REFUSE = 2
    STATUS_CHOICES = (
        (REVIEW,u'待审核'),
        (FINISH,u'通过'),
        (REFUSE,u'拒绝'),
    )

    student = models.ForeignKey(Student,on_delete=models.PROTECT,editable=False,verbose_name=u'学生')
    submit_notes = models.CharField(max_length=200,null=True,blank=True,verbose_name=u'提交备注',help_text=u'填写收款人的银行卡信息，卡号、持卡人、开户行')
    days = models.IntegerField(null=True,blank=True,verbose_name=u'缺勤天数')
    balance = models.FloatField(null=True,blank=True,verbose_name=u'退款金额')
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES,default=REVIEW,verbose_name=u'状态')
    review_notes = models.CharField(max_length=200,null=True,blank=True,verbose_name=u'审核备注')
    date = models.DateField(auto_now_add=True,null=True,blank=True,verbose_name=u'提交日期')

    class Meta:
        db_table = 'absence'
        verbose_name = u'缺勤退费申请'
        default_permissions = ()

    def to_dict(self):
        result = {
            'id':self.id,
            'student':self.student.id,
            'student_name':self.student.name,
            'submit_notes':self.submit_notes,
            'days':self.days,
            'balance':self.balance,
            'status':self.status,
            'review_notes':self.review_notes,
            'class': self.student.classes.name,
            'grade': self.student.classes.grade.name,
            'date':strfdate(self.date),
            'kinder':self.student.classes.grade.kindergarten.name
        }
        return result

