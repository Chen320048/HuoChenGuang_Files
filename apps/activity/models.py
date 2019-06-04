# coding:utf-8
from django.db import models
from DjangoUeditor.models import UEditorField

from libs.filefield import PathAndRename
from ningmeng import settings
from libs.utils import strftime



class Activity(models.Model):

    # PROCESSING = 0
    # OVER = 1
    # STATUS_CHOICES = (
    #     (PROCESSING,u'进行中'),
    #     (OVER,u'已结束')
    # )

    path_and_rename = PathAndRename('activity')
    title = models.CharField(max_length=200,null=True,blank=True,verbose_name=u'活动标题')
    # status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES,default=PROCESSING,verbose_name=u'活动状态')
    create_time = models.DateTimeField(auto_now_add=True,editable=False,verbose_name=u'发布时间')
    # close_time = models.DateTimeField(null=True,blank=True,verbose_name=u'结束时间')
    detail = UEditorField(imagePath='activity/image/',filePath='activity',default='',verbose_name=u'活动详情')
    create_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,verbose_name=u'活动发起人')

    class Meta:
        default_permissions = ()
        db_table = 'activity'
        verbose_name = u'活动管理'

    def to_dict(self):
        result = {
            'id':self.id,
            'title':self.title,
            'create_time':strftime(self.create_time),
            # 'image':self.image.url if self.image else '',
            'detail':self.detail,
            'create_user':self.create_user.id,
            'create_user_name':self.create_user.name
        }
        return result