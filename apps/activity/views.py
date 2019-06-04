# coding:utf-8
import traceback

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from apps.system.models import BizLog
from libs.http import JSONResponse, JSONError
from libs import utils
from forms import *

@csrf_exempt
def activity_list(request, template_name, extra_context=None):
    if not request.user.has_perm('account.manage_kindergardenor') and not request.user.has_perm('account.manage_investors'):
        raise PermissionDenied()
    return render_to_response(template_name, context_instance=RequestContext(request))

@csrf_exempt
def activity_edit_list(request, template_name, extra_context=None):
    if not request.user.has_perm('account.manage_kindergardenor'):
        raise PermissionDenied()
    form = ActivityForm()
    return render_to_response(template_name, {'form': form,}, context_instance=RequestContext(request))

@csrf_exempt
def activity_data(request):
    if not request.user.has_perm('account.manage_kindergardenor') and not request.user.has_perm('account.manage_investors'):
        raise PermissionDenied()
    q = request.POST.get('q')
    keyword = request.POST.get('keyword')
    rows = Activity.objects.all().order_by('-create_time')
    if q == 'status':
        rows = rows.filter(status=keyword)
    elif q == 'name':
        rows = rows.filter(name__icontains=keyword)
    elif q == 'title':
        rows = rows.filter(title__icontains=keyword)
    elif q == 'user':
        rows = rows.filter(create_user__name__icontains=keyword)
    rows,total = utils.get_page_data(request,rows)

    data = []
    for row in rows:
        item = row.to_dict()
        data.append(item)

    dict = {"total": total, "rows": data}
    return JSONResponse(dict)

@csrf_exempt
def activity_save(request):
    if not request.user.has_perm('account.manage_kindergardenor'):
        raise PermissionDenied()

    id = request.GET.get('id')
    if id == None:
        form = ActivityForm(request.POST)
    else:
        act = get_object_or_404(Activity, pk=id)
        form = ActivityForm(request.POST, instance=act)

    try:
        if form.is_valid():
            with transaction.atomic():
                if id == None:
                    act = form.save(commit=False)
                    act.create_user = request.user  # 活动编辑人即是活动发布人
                    act.save()
                else:
                    act = form.save()
                if id == None:
                    BizLog.objects.addnew(request.user, BizLog.INSERT, u"添加活动[%s],id=%d" % (act.title, act.id),
                                          act.to_dict())
                else:
                    BizLog.objects.addnew(request.user, BizLog.UPDATE, u"修改活动[%s],id=%d" % (act.title, act.id),
                                          act.to_dict())
                # name = 'image'
                # for file in request.FILES:
                #     filename = utils.handle_image_upload(request,Activity.path_and_rename,request.FILES[file],name,act)
                #     if file == name:
                #         act.image = filename
                #         act.save()


            return JSONResponse({'id': act.id})
        else:
            return JSONError(utils.dump_form_errors(form))
    except Exception, e:
        traceback.print_exc()
        return JSONError(unicode(e))

@csrf_exempt
def activity_control(request):
    """修改状态"""
    if not request.user.has_perm('account.manage_kindergardenor'):
        raise PermissionDenied()

    pk = request.GET.get('id')
    status = request.GET.get('status')

    act = get_object_or_404(Activity, pk=int(pk))
    if status == act.status:  # 禁止对活动进行重复修改
        return JSONResponse({})
    act.status = status
    if int(status) == Activity.PROCESSING:
        act.close_time = None
    if int(status) == Activity.OVER:
        act.close_time = timezone.now()
    act.save()

    status_text = status and u'主动开启活动' or u'主动关闭活动'
    BizLog.objects.addnew(request.user, BizLog.UPDATE, u"%s[%s],id=%d" % (status_text, act.name, act.id))
    return JSONResponse({})

