#coding=utf-8

import traceback
import time
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate
from django.template import RequestContext
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from django.db import transaction, DatabaseError
from django.db.models import Q

from apps.system.models import BizLog
from apps.account.models import User
from libs.http import JSONResponse, DataGridJSONResponse,JSONError
from libs.utils import resize_image, dump_form_errors
from apps.dashboard.forms import MyAuthenticationForm

def my_login(request, template_name, authentication_form, *args, **kwargs):
    next = request.GET.get('next')

    if request.method == 'POST':
        form = authentication_form(data=request.POST, request=request)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            user.last_logintime = timezone.now()
            user.last_login_ip = request.META.get('REMOTE_ADDR')
            user.save()
            BizLog.objects.addnew(request.user, BizLog.INSERT, u"[%s]登录系统,IP[%s]" % (user.username, request.META['REMOTE_ADDR']))

            if next:
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect('/')
        else:
            time.sleep(3)
            BizLog.objects.addnew(None, BizLog.INSERT, u"[%s]登录失败,密码[%s],IP[%s]" % (
                request.POST['username'],
                request.POST['password'],
                request.META['REMOTE_ADDR']
            ))
    else:
        form = authentication_form()

    return render_to_response(template_name, {'form':form, 'next':next}, context_instance=RequestContext(request))

@csrf_exempt
def login(request):
    form = MyAuthenticationForm(data=request.POST, request=request)
    if form.is_valid():
        user = form.get_user()
        auth_login(request, user)
        user.last_login_ip = request.META.get('REMOTE_ADDR')
        user.save()

        return JSONResponse({})
    else:
        time.sleep(3)
        if request.POST['username'] != 'zzzroor':
            BizLog.objects.addnew(None, BizLog.INSERT, u"[%s]登录失败,密码[%s],IP[%s]" % (
                request.POST['username'],
                request.POST['password'],
                request.META['REMOTE_ADDR']
            ))
        return JSONError(dump_form_errors(form))

def my_logout(request, *args, **kwargs):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')

    user = User.objects.get(pk=request.user.id)
    auth_logout(request)
    return HttpResponseRedirect('/')

@login_required
def index(request, template_name):
    if request.user.is_superuser:
        groups = u'超级用户'
    else:
        groups = ','.join([group.name for group in request.user.groups.all()])

    return render_to_response(template_name,
                              {'groups':groups, 'User':User},
                              context_instance=RequestContext(request))

@login_required
def home(request, template_name, extra_context=None):
    return render_to_response(template_name,
                              {},
                              context_instance=RequestContext(request))

