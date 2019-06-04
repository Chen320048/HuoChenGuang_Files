# coding=utf-8

import math

from django.db import models, connection
from django.db.models import Count, Avg
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group
from django.utils import timezone
from django.conf import settings

from libs.utils import strftime, strfdate, year_delta
from libs.filefield import PathAndRename
from apps.classes.models import Kindergarten,Grade,Classes

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError(u'请输入用户名')
        user = self.model(username=username,last_login=timezone.now(), **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        u = self.create_user(username, password, **extra_fields)
        u.is_active = True
        u.is_superuser = True
        u.type = User.ADMINISTRATOR
        u.save(using=self._db)
        return u


class User(AbstractBaseUser, PermissionsMixin):
    ADMINISTRATOR = 0
    COMPANY = 1
    INVESTORS = 2
    KINDERGARTENOR = 3
    TEACHER = 4
    TYPE_CHOICES = (
        (ADMINISTRATOR, u'管理员'),
        (COMPANY,u'园企账号'),
        (INVESTORS,u'投资人'),
        (KINDERGARTENOR,u'园长'),
        (TEACHER,u'教师'),
    )
    username = models.CharField(verbose_name=u'帐号', max_length=30, unique=True, db_index=True)
    name = models.CharField(verbose_name=u'姓名', max_length=100, null=True, blank=True)
    type = models.PositiveSmallIntegerField(u'类别', choices=TYPE_CHOICES, default=ADMINISTRATOR)
    is_active = models.BooleanField(verbose_name=u'状态', default=True)
    time_locked = models.DateTimeField(verbose_name=u'锁定时间', null=True, blank=True, editable=False)
    date_joined = models.DateTimeField(verbose_name=u'注册时间', auto_now_add=True, editable=False)
    last_login_ip = models.GenericIPAddressField(verbose_name=u'最后登录IP', null=True, editable=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return self.username

    class Meta:
        db_table = "auth_user"
        verbose_name = u"账号"

        unique_together = [
            ('username', 'type')
        ]

        default_permissions = ()
        permissions = (
            ('manage_investors',u'投资人'),  # 查看活动
            ('manage_company',u'园企'),  # 添加幼儿园、园长、添加修改投资人、添加修改科目
            ('manage_kindergardenor',u'幼儿园园长'),  # 添加修改年班级,添加修改学生,添加修改教师,添加收支,活动添加编辑
            ('manage_teacher',u'教师')  # 添加修改学生,添加修改学生考勤
        )

    def to_dict(self):
        result = {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'type': self.type,
            'type_text': self.get_type_display(),
            'is_superuser': self.is_superuser,
            'is_active': self.is_active,
            'last_login': strftime(self.last_login),
            'last_login_ip':self.last_login_ip,
            'time_locked': self.time_locked and strftime(self.time_locked) or '',
            'date_joined': strftime(self.date_joined),
        }
        return result

    def to_teacher_dict(self):
        result = self.to_dict()
        try:
            result.update(self.bind_teacher.to_dict())
        except:
            pass
        return result

    def __unicode__(self):
        return self.name


class KindergartenManager(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,editable=False,related_name='bind_kindergartenor',on_delete=models.CASCADE,verbose_name=u'用户')
    kindergarten = models.ForeignKey(Kindergarten,related_name=u'kinder_managers',on_delete=models.PROTECT,verbose_name=u'所属幼儿园')

    class Meta:
        default_permissions = ()
        db_table = 'auth_kindergarten_manager'
        verbose_name = u'幼儿园园长'

    def to_dict(self):
        result = self.user.to_dict()
        result['kindergarten'] = self.kindergarten_id
        result['kindergarten_name'] = self.kindergarten.name
        return result

class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,editable=False,related_name='bind_teacher',on_delete=models.CASCADE)
    classes = models.ForeignKey(Classes,related_name=u'class_teacher',on_delete=models.PROTECT,verbose_name=u'所属班级')
    create_time = models.DateTimeField(auto_now_add=True,editable=False,verbose_name=u'添加时间')

    class Meta:
        default_permissions = ()
        db_table = 'auth_teacher'
        verbose_name = u'教师管理'

    def to_dict(self):

        result = self.user.to_dict()
        result['classes'] = self.classes_id
        result['classes_name'] = self.classes.name
        result['grade'] = self.classes.grade_id
        result['grade_name'] = self.classes.grade.name
        return result
