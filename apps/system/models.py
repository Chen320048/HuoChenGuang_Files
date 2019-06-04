# coding=utf8

from django.db import models
from django.conf import settings
from django.utils import timezone
from libs.utils import strftime, strftime_s
from libs.filefield import PathAndRename

import json


class BizLogManager(models.Manager):
    def addnew(self, user, type, description, data=None):
        row = self.model(user=user, type=type, description=description, create_time=timezone.now())
        if data:
            row.data = json.dumps(data)
        row.save()
        return row


class BizLog(models.Model):
    INSERT = 1
    UPDATE = 2
    DELETE = 3
    IMPORT = 4
    EXPORT = 5
    PRINT = 6
    CHECK = 7
    TYPE_CHOICES = (
        (INSERT, u'添加'),
        (UPDATE, u'修改'),
        (DELETE, u'删除'),
        (IMPORT, u'导入'),
        (EXPORT, u'导出'),
        (PRINT, u'打印'),
        (CHECK, u'审核'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, verbose_name=u"类别")
    description = models.CharField(max_length=100, verbose_name=u"内容")
    data = models.TextField(max_length=5000, verbose_name=u"数据", null=True, blank=True)
    create_time = models.DateTimeField(verbose_name=u"添加时间", auto_now_add=True, editable=False)

    objects = BizLogManager()

    def to_dict(self):
        result = {
            'id': self.id,
            'type': self.type,
            'type_text': self.get_type_display(),
            'user':self.user and self.user.id or None,
            'user_text':self.user and self.user.username or '',
            'description': self.description,
            'create_time': strftime(self.create_time)
        }
        return result

    class Meta:
        default_permissions = ()
        db_table = "system_log"
        ordering = ['-id']
        verbose_name = u"系统"
        permissions = (
            ("view_visitor", "访问终端统计"),
            ("manage_version", "版本管理"),
            ("view_feedback", "建议反馈"),
            ("view_log", "系统日志"),
            ("manage_vcode", "系统验证码管理"),
        )

class Feedback(models.Model):
    IDEA = 1
    DATAERROR = 2
    BUG = 3
    TYPE_CHOICES = (
        (IDEA, u'建议'),
        (DATAERROR, u'数据错误'),
        (BUG, u'程序bug'),
    )

    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, verbose_name=u"类别")
    content = models.CharField(u'内容', max_length=1000)
    create_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='feedback_ref_user', verbose_name=u"帐号",
                                    on_delete=models.PROTECT)
    create_time = models.DateTimeField(verbose_name=u"时间", auto_now_add=True, editable=False)
    reply_content = models.CharField(u'回复内容', max_length=1000, null=True, blank=True, editable=False)
    reply_time = models.DateTimeField(verbose_name=u"回复时间", editable=False, null=True, blank=True)
    reply_read = models.BooleanField(verbose_name=u"回复已被阅读", editable=False, default=False)

    def to_dict(self):
        result = {
            'id': self.id,
            'type': self.type,
            'type_text': self.get_type_display(),
            'content': self.content,
            'create_user': self.create_user.id,
            'create_user_text': self.create_user.username,
            'create_time': strftime(self.create_time),
            'reply_content': self.reply_content,
            'reply_time': strftime(self.reply_time),
            'reply_read': self.reply_read
        }
        return result

    class Meta:
        default_permissions = ()
        verbose_name = "用户反馈"
        db_table = "system_feedback"
        ordering = ['-id']


path_and_rename = PathAndRename("upgrade")


class Version(models.Model):
    ANDROID = 0
    PLATFORM_CHOICES = (
        (ANDROID, '会员端'),
    )

    platform = models.IntegerField(choices=PLATFORM_CHOICES, verbose_name="平台", default=0)
    version = models.CharField(max_length=5, verbose_name="版本号")
    filename = models.FileField("文件", upload_to=path_and_rename, blank=True)
    title = models.CharField(max_length=100, verbose_name="标题")
    content = models.CharField(max_length=200, verbose_name="内容")
    created = models.DateTimeField(auto_now=True, verbose_name="发布时间")
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __unicode__(self):
        return self.title

    def _format_created(self):
        return self.created.strftime('%Y-%m-%d %H:%M:%S')

    created_formated = property(_format_created)

    class Meta:
        default_permissions = ()
        ordering = ['-id']
        verbose_name = "版本信息"
        unique_together = ("platform", "version")


class Visitor(models.Model):
    platform = models.CharField(max_length=20, blank=True, verbose_name="设备类型")
    device_UID = models.CharField(max_length=64, blank=True, verbose_name="设备编号")
    device_machine = models.CharField(max_length=20, blank=True, verbose_name="设备型号")
    os_version = models.CharField(max_length=20, blank=True, verbose_name="系统版本")
    app_version = models.CharField(max_length=20, blank=True, verbose_name="App版本")
    resolution = models.CharField(max_length=20, blank=True, verbose_name="分辨率")
    network_type = models.CharField(max_length=20, blank=True, verbose_name="网络类型")
    IP = models.CharField(max_length=20, blank=True, verbose_name="客户端IP")
    start_time = models.DateTimeField(verbose_name="登录时间")
    end_time = models.DateTimeField(verbose_name="登出时间")
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    def to_dict(self):
        result = {
            'id': self.id,
            'platform': self.platform,
            'device_UID': self.device_UID,
            'device_machine': self.device_machine,
            'os_version': self.os_version,
            'app_version': self.app_version,
            'resolution': self.resolution,
            'network_type': self.network_type,
            'IP': self.IP,
            'start_time': strftime(self.start_time),
            'end_time': strftime(self.end_time),
            'user': self.user.id,
            'user_text': self.user.username,
        }
        return result

    @staticmethod
    def get_export_headers():
        result = (u'设备类型', u'设备编号', u'设备型号', u'系统版本', u'App版本', u'分辨率', u'网络类型', u'客户端IP',
                  u'登录时间', u'登出时间', u'用户名',)
        return result

    def to_export_data(self):
        result = (
            self.platform, self.device_UID, self.device_machine, self.os_version, self.app_version,
            self.resolution, self.network_type, self.IP, strftime(self.start_time), strftime(self.end_time), self.user.username,)
        return result

    class Meta:
        default_permissions = ()
        db_table = "system_visitor"
        ordering = ['-id']


class VCode(models.Model):
    """验证码"""
    REGISTER = 'SMS_116560769'
    CHANGE_PASSWORD = 'SMS_112875079'
    INFO_CHANGED = 'SMS_112875078'
    LOGIN_EXCEPTION = 'SMS_112875081'
    LOGIN_CONFIRM = 'SMS_112875082'
    MESSAGE_TEST = 'SMS_112875083'
    IDENTITY_VERIFICATION = 'SMS_112875084'
    TYPE_CHOICES = (
        (REGISTER, u'注册'),
        (CHANGE_PASSWORD, u'修改密码'),
    )
    OK = 0
    UNSUCCESS = 1
    STATUS_CHOICES = (
        (OK, u'发送成功'),
        (UNSUCCESS, u'发送失败'),
    )
    vcode = models.CharField('验证码', max_length=4)
    mobile = models.CharField('手机号', max_length=11)
    add_time = models.DateTimeField('时间', auto_now_add=True)
    type = models.CharField(choices=TYPE_CHOICES, max_length=20, verbose_name=u"用途", editable=False,
                                                  default=REGISTER)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, verbose_name=u"状态", editable=False,
                                                  default=OK)

    class Meta:
        default_permissions = ()
        db_table = "system_vcode"
        ordering = ['-id']


    def to_dict(self):
        result = {}
        result['mobile'] = self.mobile
        result['vcode'] = self.vcode
        result['add_time'] = strftime(self.add_time)
        result['type'] = self.type
        result['type_text'] = self.get_type_display()
        result['status'] = self.status
        result['status_text'] = self.get_status_display()
        return result


class Token(models.Model):
    """柠檬云全局access_token"""
    appid = models.IntegerField(verbose_name='AppID')
    appsecret = models.CharField(verbose_name='App秘钥', max_length=255)
    token = models.CharField(verbose_name='全局token', editable=False, max_length=255)
    valid_term = models.PositiveIntegerField(verbose_name='有效时长', editable=False)
    update_time = models.DateTimeField(verbose_name='上次更改时间', auto_now=True)

    class Mete:
        default_permissions = ()
        db_table = "system_token"
        verbose_name = "全局token"

    def to_dict(self):
        result = {
            'appid': self.appid,
            'appsecret': self.appsecret,
            'token': self.token,
            'valid_term': self.valid_term,
            'update_time': strftime_s(self.update_time)
        }
        return result



