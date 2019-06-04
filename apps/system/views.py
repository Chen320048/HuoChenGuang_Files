# coding=utf8

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from libs.http import JSONResponse, JSONError
from libs import utils
from models import Feedback, BizLog, Version, Visitor, path_and_rename, VCode, Token
from forms import ChangePasswordForm, FeedbackForm, VersionForm, ResetPasswordForm
from apps.account.models import User
from django.db.models import Q

import traceback
import tablib
import datetime
import requests

@csrf_exempt
# @user_passes_test(lambda u: u.is_superuser)
@login_required
def change_password(request, template_name, extra_context=None):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        form.username = request.user.username
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()
            return render_to_response(template_name, {'success': 'true', 'form': form},
                                      context_instance=RequestContext(request))
    else:
        form = ChangePasswordForm()
    return render_to_response(template_name, {'form': form}, context_instance=RequestContext(request))


@csrf_exempt
def reset_password(request, template_name, extra_context=None):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user = User.objects.get(username=form.cleaned_data['username'])
            user.set_password(form.cleaned_data['new_password'])
            return JSONResponse({})
        else:
            return JSONError(utils.dump_form_errors(form))
    else:
        form = ResetPasswordForm()
    return render_to_response(template_name, {'form': form}, context_instance=RequestContext(request))


@login_required
@permission_required('system.view_feedback')
def feedback_home(request, template_name, extra_context=None):
    form = FeedbackForm(initial={'create_user': request.user.id})
    return render_to_response(template_name, {'form': form}, context_instance=RequestContext(request))


@csrf_exempt
@permission_required('system.view_feedback')
def feedback_data(request):
    rows = Feedback.objects.filter()
    if not request.user.is_superuser:
        rows = rows.filter(create_user=request.user)

    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        data.append(row.to_dict())

    dict = {"total": total, "rows": data}
    return JSONResponse(dict)


@csrf_exempt
@permission_required('system.view_feedback')
def feedback_mine_data(request):
    # 修改读取状态
    Feedback.objects.filter(create_user=request.user).update(reply_read=True)

    # 显示相关数据
    rows = Feedback.objects.filter(create_user=request.user)

    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        data.append(row.to_dict())

    dict = {"total": total, "rows": data}
    return JSONResponse(dict)


@csrf_exempt
@permission_required('system.view_feedback')
def feedback_save(request):
    id = request.GET.get('id')

    if id == None:
        form = FeedbackForm(request.POST)
    else:
        instance = get_object_or_404(Feedback, pk=id)
        form = FeedbackForm(request.POST, instance=instance)

    try:
        if form.is_valid():
            instance = form.save()
            return JSONResponse({'id': instance.id})
        else:
            return JSONError(utils.dump_form_errors(form))
    except Exception, e:
        return JSONError(unicode(e))


@csrf_exempt
@permission_required('system.view_feedback')
def feedback_delete(request):
    id = request.GET.get('id')
    instance = get_object_or_404(Feedback, pk=id)
    instance.delete()
    return JSONResponse({})


@csrf_exempt
@permission_required('system.view_feedback')
def feedback_reply(request):
    id = request.POST.get('id')
    content = request.POST.get('content')

    instance = get_object_or_404(Feedback, pk=id)
    instance.reply_content = content
    instance.reply_time = timezone.now()
    instance.save()

    return JSONResponse({})


@permission_required('system.view_log')
def log_home(request, template_name, extra_context=None):
    return render_to_response(template_name, {'types': BizLog.TYPE_CHOICES}, context_instance=RequestContext(request))


@csrf_exempt
@permission_required('system.view_log')
def log_list(request):
    rows = BizLog.objects.filter()

    q = request.POST.get('q')
    keyword = request.POST.get('keyword')
    if keyword and len(keyword) > 0:
        if q == 'type':
            rows = rows.filter(type=int(keyword))
        elif q == 'name':
            rows = rows.filter(user__username__contains=keyword)
        elif q == 'description':
            rows = rows.filter(description__contains=keyword)

    date_begin = request.POST.get('date_begin')
    date_end = request.POST.get('date_end')
    if date_begin:
        rows = rows.filter(create_time__gte=date_begin)
    if date_end:
        rows = rows.filter(create_time__lte=date_end + " 23:59:59")

    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        data.append(row.to_dict())

    result = {
        'rows': data,
        'total': total,
    }
    return JSONResponse(result)


@permission_required('system.manage_version')
def version_list(request, template_name, extra_context=None):
    return render_to_response(template_name, context_instance=RequestContext(request))


@csrf_exempt
@permission_required('system.manage_version')
def version_data(request):
    rows = Version.objects.all()
    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        item = {'id': row.id, 'platform': row.get_platform_display(), 'version': row.version,
                'title': row.title, 'content': row.content,
                'created': row.created_formated, 'username': row.user.username}
        data.append(item)

    dict = {"total": total, "rows": data}
    return JSONResponse(dict)


@permission_required('system.manage_version')
def version_add(request, template_name, extra_context=None):
    if request.method == "POST":
        form = VersionForm(request.POST)

        if form.is_valid():
            with transaction.atomic():
                ver = form.save()

                # if form.cleaned_data['platform'] == 1:
                filename = "%s/chenshi.apk" % (path_and_rename.path)
                full_filename = "%s/%s" % (settings.MEDIA_ROOT, filename)

                f = request.FILES.get("filename")
                file = open(full_filename, "wb")
                for chunk in f.chunks():
                    file.write(chunk)
                file.close()

                ver.filename = filename
                ver.save()

            return HttpResponseRedirect('/system/version/list/')
    else:
        form = VersionForm(initial={'user': request.user})

    return render_to_response(template_name, {'form': form}, context_instance=RequestContext(request))


@csrf_exempt
@permission_required('system.manage_version')
def version_delete(request):
    try:
        ids = request.POST.get('ids')
        Version.objects.extra(where=['id IN (' + ids + ')']).delete()
    except Exception, e:
        return JSONError(str(e))

    return JSONResponse({})


@permission_required('system.view_visitor')
def vistor_list(request, template_name, extra_context=None):
    return render_to_response(template_name, context_instance=RequestContext(request))


@csrf_exempt
@permission_required('system.view_visitor')
def vistor_data(request):
    """来访记录数据"""
    start_time = request.POST.get("start_time")
    end_time = request.POST.get("end_time")
    username = request.POST.get("username")

    rows = Visitor.objects.all()
    # 组合搜索条件
    if start_time != None and start_time != "":
        rows = rows.filter(start_time__gte=start_time)

    if end_time != None and end_time != "":
        rows = rows.filter(end_time__lte=end_time)

    if username != None and username != "":
        rows = rows.filter(user__username__contains=username)

    if request.POST.get('export') == None:
        rows, total = utils.get_page_data(request, rows)

        # 组合json数据
        data = []
        for row in rows:
            data.append(row.to_dict())
        dict = {"total": total, "rows": data}
        return JSONResponse(dict)
    else:
        data = []
        for row in rows:
            data.append(row.to_export_data())
        data = tablib.Dataset(*data, headers=Visitor.get_export_headers())

        filename = settings.TMP_ROOT + "/export.csv"
        open(filename, 'wb').write(data.xls)

        response = HttpResponse(utils.read_file(filename), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=export.xls'

        BizLog.objects.addnew(request.user, BizLog.EXPORT, u"导出客户端访问记录数据")

        return response


@permission_required('system.manage_vcode')
def vcode_list(request, template_name, extra_context=None):
    return render_to_response(template_name, context_instance=RequestContext(request))


@csrf_exempt
@permission_required('system.manage_vcode')
def vcode_data(request):
    start_time = request.POST.get("start_time")
    end_time = request.POST.get("end_time")
    username = request.POST.get("username")

    rows = VCode.objects.all()
    # 组合搜索条件
    if start_time != None and start_time != "":
        rows = rows.filter(add_time__gte=start_time)

    if end_time != None and end_time != "":
        rows = rows.filter(add_time__lte=end_time)

    if username != None and username != "":
        rows = rows.filter(mobile=username)

    if request.POST.get('export') == None:
        rows, total = utils.get_page_data(request, rows)

        # 组合json数据
        data = []
        for row in rows:
            data.append(row.to_dict())
        dict = {"total": total, "rows": data}
        return JSONResponse(dict)
    else:
        data = []
        for row in rows:
            data.append(row.to_export_data())
        data = tablib.Dataset(*data, headers=Visitor.get_export_headers())

        filename = settings.TMP_ROOT + "/export.csv"
        open(filename, 'wb').write(data.xls)

        response = HttpResponse(utils.read_file(filename), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=export.xls'
        return response

def get_new_token():
    url = settings.MAIN_DOMAIN + '/api/oauth2/AccessToken'
    date = {
        'appid': 10051,
        'appsecret': '123456'
    }
    response = requests.get(url=url, params=date)
    result = response.json()
    try:
        token_obj = Token.objects.get(appid=10051)
        token_obj.token = result['access_token']
        token_obj.valid_term = result['expires_in']
        token_obj.save()
    except:
        dic = date
        dic['token'] = result['access_token']
        dic['valid_term'] = result['expires_in']
        Token.objects.create(**dic)
    return result['access_token']


def get_token():
    token_obj = Token.objects.filter(appid=10051)
    if len(token_obj) == 0:
        token = get_new_token()
    else:
        token_obj = token_obj[0]
        token_info = token_obj.to_dict()
        update_time = token_info['update_time']
        valid_term = token_info['valid_term']
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        now_time = datetime.datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')
        update_time = datetime.datetime.strptime(update_time, '%Y-%m-%d %H:%M:%S')
        if valid_term > (now_time - update_time).seconds:
            token = token_info['token']
        else:
            token = get_new_token()
    return token


