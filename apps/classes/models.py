# coding:utf-8
from django.db import models
from django.conf import settings

from libs.filefield import PathAndRename


class Kindergarten(models.Model):
    path_and_rename = PathAndRename('kindergarten')
    name = models.CharField(max_length=20, verbose_name=u'幼儿园名字')
    address = models.CharField(max_length=200, null=True, blank=True, verbose_name=u'幼儿园地址')
    notes = models.TextField(null=True, blank=True, verbose_name=u'备注信息')
    account_book = models.CharField(max_length=50, verbose_name=u'账套')

    class Meta:
        db_table = 'kindergarten'
        verbose_name = u'幼儿园管理'
        default_permissions = ()
    def to_dict(self):
        result = {
            'id':self.id,
            'name':self.name,
            'address':self.address,
            'notes':self.notes,
            'account_book':self.account_book,
            'kindergartenor':','.join( i.user.name for i in (self.kinder_managers.all()))
        }
        return result




class Grade(models.Model):
    name = models.CharField(max_length=10, verbose_name=u'年级名')
    introduction = models.CharField(max_length=200, verbose_name=u'年级介绍')
    kindergarten = models.ForeignKey(Kindergarten,related_name=u'kinder_grades', on_delete=models.PROTECT,verbose_name=u'幼儿园')

    class Meta:
        default_permissions = ()
        db_table = 'grade'
        verbose_name = u'年级管理'

    def to_dict(self):
        result = {
            'id':self.id,
            'name':self.name,
            'introduction':self.introduction,
            'kindergarten':self.kindergarten.name
        }
        return result

    def __unicode__(self):
        return self.name


class Classes(models.Model):
    name = models.CharField(max_length=10, verbose_name=u'班级名')
    introduction = models.CharField(max_length=200, verbose_name=u'班级介绍')
    grade = models.ForeignKey(Grade, related_name=u'grade_classes', on_delete=models.PROTECT,verbose_name=u'年级')

    class Meta:
        default_permissions = ()
        db_table = 'classes'
        verbose_name = u'班级管理'

    def to_dict(self):
        result = {
            'id':self.id,
            'name':self.name,
            'introduction':self.introduction,
            'teacher':','.join(teacher.user.name for teacher in self.class_teacher.all()),
            # 'quantity':self.classes_students.count()
        }
        return result

    def __unicode__(self):
        return self.name

class Student(models.Model):
    FEMALE = 1
    MALE = 0
    GENDER_CHOICES = (
        (MALE, u'男'),
        (FEMALE, u'女'),
    )
    path_and_rename = PathAndRename('user/student')
    name = models.CharField(max_length=10,verbose_name=u'名字',null=True,blank=True)
    # icon = models.ImageField(upload_to=path_and_rename, null=True, blank=True,verbose_name=u'头像')
    age = models.IntegerField(null=True,blank=True,verbose_name=u'年龄')
    gender = models.PositiveSmallIntegerField(choices=GENDER_CHOICES, verbose_name=u"性别", default=MALE)
    classes = models.ForeignKey(Classes,null=True,blank=True,related_name=u'classes_students',on_delete=models.PROTECT,verbose_name=u'班级')
    notes = models.CharField(max_length=200,null=True,blank=True,verbose_name=u'备注信息')

    class Meta:
        default_permissions = ()
        db_table = 'student'
        verbose_name = u'学生'

    def to_dict(self):
        from apps.account.models import Teacher
        result = {
            'id':self.id,
            'name':self.name,
            'age':self.age,
            'gender':self.gender,
            'gender_text':self.get_gender_display(),
            'classes':self.classes_id,
            'classes_name':self.classes and self.classes.name or "",
            'notes':self.notes,
            'grade':self.classes and self.classes.grade and self.classes.grade.name or "",
            'teacher':','.join(teacher.user.name for teacher in (Teacher.objects.filter(classes=self.classes)))
        }
        return result

