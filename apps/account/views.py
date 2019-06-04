# coding=utf-8

from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.utils.decorators import method_decorator
from django.db import transaction, IntegrityError
from django.db.models import Q, Sum
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import Group, Permission
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.conf import settings
from django.core.exceptions import PermissionDenied

from models import User,KindergartenManager,Teacher
from apps.classes.models import Kindergarten, Grade
from forms import *
from libs.http import JSONResponse, JSONError
from libs import utils
from apps.system.models import BizLog

import traceback
import qrcode
import os

@csrf_exempt
@permission_required('account.manage_company')
def account_administrator(request, template_name, extra_context=None):
    if request.path == u'/account/investors/':
        form = AccountForm(initial={'type':User.INVESTORS})  # 为表单的隐藏字段type初始化一个值,使添加修改用户时type始终默认
    if request.path == u'/account/company/':
        form = AccountForm(initial={'type':User.COMPANY})
    form_change = ChangeAccountForm()  # 模板未用到
    return render_to_response(template_name,{'form': form, 'form_change': form_change,},context_instance=RequestContext(request))


@csrf_exempt
@permission_required('account.manage_company')
def account_data(request):
    q = request.POST.get('q')  # js search()函数的参数,在这里用来作为搜索字段
    keyword = request.POST.get('keyword') # 搜索的关键字

    type = request.GET.get('type', User.ADMINISTRATOR)

    rows = User.objects.filter(type=type).order_by("-id")
    if type == User.ADMINISTRATOR:
        rows = rows.exclude(username='root')

    if keyword and len(keyword) > 0:
        if q == 'name':
            rows = rows.filter(name__icontains=keyword)
        elif q == 'username':
            rows = rows.filter(username__icontains=keyword)
        elif q == 'is_active':
            rows = rows.filter(is_active=int(keyword))

    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        item = row.to_dict()
        # groups = row.groups.all()
        # item['groups'] = [group.id for group in groups]
        # item['groups_name'] = ','.join(group.name for group in groups)
        data.append(item)

    dict = {"total": total, "rows": data}
    return JSONResponse(dict)


@csrf_exempt
@permission_required('account.manage_company')
def account_save(request):
    """保存用户帐号"""
    id = request.GET.get('id')

    if id == None:
        form = AccountForm(request.POST)
    else:
        user = get_object_or_404(User, pk=id)
        form = ChangeAccountForm(request.POST, instance=user)

    try:
        if form.is_valid():
            with transaction.atomic():
                if id == None:
                    user = User.objects.create_user(form.cleaned_data['username'],
                                                    form.cleaned_data['password'],
                                                    type=form.cleaned_data['type'],
                                                    name=form.cleaned_data['name'],
                                                    is_active=form.cleaned_data['is_active'],
                                                    )
                    if form.cleaned_data['type'] == User.COMPANY:
                        perms = Permission.objects.filter(codename__in=['manage_company',])  # 由于不确定后续是否对该类型用户添加多个权限,因此使用__in的过滤方法
                    elif form.cleaned_data['type'] == User.INVESTORS:
                        perms = Permission.objects.filter(codename__in=['manage_investors', ])
                    user.user_permissions.set(perms)  # 未用户添加(多个)权限(set(查询集))
                    BizLog.objects.addnew(request.user, BizLog.INSERT, u"添加帐号[%s],id=%d" % (user.username, user.id),
                                          user.to_dict())
                else:
                    user = form.save()
                    BizLog.objects.addnew(request.user, BizLog.UPDATE, u"修改帐号[%s],id=%d" % (user.username, user.id),
                                          user.to_dict())
            return JSONResponse({'id': user.id})
        else:
            return JSONError(utils.dump_form_errors(form))
    except Exception, e:
        traceback.print_exc()
        return JSONError(unicode(e))


@csrf_exempt
@user_passes_test(lambda u: u.is_superuser)
def account_delete(request):
    """删除帐号"""
    id = request.GET.get('id')
    user = get_object_or_404(User, pk=id)
    if user.username != 'root':
        try:
            with transaction.atomic():
                s = u"删除用户帐号[%s],id=%d" % (user.username, user.id)
                BizLog.objects.addnew(request.user, BizLog.DELETE, s)
                user.delete()
        except Exception, e:
            traceback.print_exc()
            return JSONError(unicode(e))

    return JSONResponse({})

@csrf_exempt
@login_required
def change_password(request):
    """修改密码"""
    id = request.POST.get('id')
    user = get_object_or_404(User, pk=id)
    user.set_password(request.POST.get('password'))
    user.save()
    BizLog.objects.addnew(request.user, BizLog.UPDATE, u"修改密码[%s],id=%d" % (user.username, user.id))
    return JSONResponse({})


@csrf_exempt
def change_active(request):
    """修改状态"""
    if not request.user.has_perm('account.manage_employee') \
            and not request.user.has_perm('account.manage_member'):
        raise PermissionDenied()

    pk = request.GET.get('id')
    status = request.GET.get('status') == 'true' and True or False

    user = get_object_or_404(User, pk=int(pk))
    user.is_active = status
    user.save()

    status_text = status and u'解禁账号' or u'禁用帐号'
    BizLog.objects.addnew(request.user, BizLog.UPDATE, u"%s[%s],id=%d" % (status_text, user.username, user.id))
    return JSONResponse({})


@csrf_exempt
@permission_required('account.manage_company')
def kindergartenor_list(request, template_name, extra_context=None):
    """幼儿园园长"""
    kindergartens = Kindergarten.objects.all()
    form = KindergartenManagerForm(initial={'type':User.KINDERGARTENOR})
    return render_to_response(template_name, {'form': form,'kindergartens':kindergartens}, context_instance=RequestContext(request))


@csrf_exempt
@permission_required('account.manage_company')
def kindergartenor_data(request):
    """幼儿园园长数据"""
    q = request.POST.get('q')
    keyword = request.POST.get('keyword')

    rows = KindergartenManager.objects.all().order_by("-id")

    if keyword and len(keyword) > 0:
        if q == 'name':
            rows = rows.filter(user__name__icontains=keyword)
        elif q == 'username':
            rows = rows.filter(user__username__icontains=keyword)
        elif q == 'is_active':
            rows = rows.filter(user__is_active=int(keyword))
        elif q == 'kindername':
            rows = rows.filter(kindergarten__id=keyword)
        elif q == 'gender':
            rows = rows.filter(user__gender=keyword)


    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        item = row.to_dict()
        groups = row.user.groups.all()
        item['groups'] = [group.id for group in groups]
        item['groups_name'] = ','.join(group.name for group in groups)
        data.append(item)  # item的key注意和模板table的field保持一致性,包括forms类的字段

    dict = {"total": total, "rows": data}
    return JSONResponse(dict)


@csrf_exempt
@permission_required('account.manage_company')
def kindergartenor_save(request):
    id = request.GET.get('id')

    if id == None:
        form = KindergartenManagerForm(request.POST)
    else:
        user = get_object_or_404(User, pk=id)
        form = ChangeKindergartenManagerForm(request.POST, instance=user)

    try:
        if form.is_valid():
            with transaction.atomic():
                if id == None:
                    user = User.objects.create_user(form.cleaned_data['username'],
                                                    form.cleaned_data['password'],
                                                    name=form.cleaned_data['name'],
                                                    is_active=form.cleaned_data['is_active'],
                                                    type=form.cleaned_data['type']
                                                    )
                    perms = Permission.objects.filter(codename__in=['manage_kindergardenor',])
                    user.user_permissions.set(perms)
                    kindergartenor = KindergartenManager.objects.create(user=user,kindergarten_id=form.data['kindergarten'])
                    kindergartenor.save()

                    BizLog.objects.addnew(request.user, BizLog.INSERT, u"添加幼儿园园长帐号[%s],id=%d" % (user.username, user.id),
                                          user.to_dict())
                else:
                    user = form.save()
                    kindergartenor = user.bind_kindergartenor
                    kindergartenor.kindergarten_id = form.data['kindergarten']
                    kindergartenor.save()
                    BizLog.objects.addnew(request.user, BizLog.UPDATE, u"修改幼儿园园长帐号[%s],id=%d" % (user.username, user.id),
                                          kindergartenor.to_dict())
            return JSONResponse({'id': user.id})
        else:
            return JSONError(utils.dump_form_errors(form))
    except Exception, e:
        traceback.print_exc()
        return JSONError(unicode(e))


@csrf_exempt
@permission_required('account.manage_kindergardenor')
def teacher_list(request, template_name, extra_context=None):

    form = TeacherForm()
    classes = Classes.objects.all()
    grade = Grade.objects.all()
    if request.user.type == User.KINDERGARTENOR:  # 当前幼儿园园长下的幼儿园班年级
        classes = classes.filter(grade__kindergarten=request.user.bind_kindergartenor.kindergarten)
        grade = grade.filter(kindergarten=request.user.bind_kindergartenor.kindergarten)
    return render_to_response(template_name, {'form': form,'class':classes,'grade':grade}, context_instance=RequestContext(request))


@csrf_exempt
@permission_required('account.manage_kindergardenor')
def teacher_data(request):
    """已登录幼儿园园长查看当前幼儿园所有教师信息"""
    q = request.POST.get('q')
    keyword = request.POST.get('keyword')
    rows = Teacher.objects.all()
    if request.user.type == User.KINDERGARTENOR:
        rows = rows.filter(classes__grade__kindergarten=request.user.bind_kindergartenor.kindergarten).order_by('-id')
    if keyword and len(keyword) > 0:
        if q == 'username':
            rows = rows.filter(user__username__icontains=keyword)
        elif q == 'name':
            rows = rows.filter(user__name__icontains=keyword)
        elif q == 'is_active':
            rows = rows.filter(user__is_active=int(keyword))
        elif q == 'grade':
            rows = rows.filter(classes__grade_id=keyword)
        elif q == 'class':
            rows = rows.filter(classes_id=keyword)


    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        item = row.to_dict()
        data.append(item)

    dict = {"total": total, "rows": data}
    return JSONResponse(dict)


@csrf_exempt
@permission_required('account.manage_kindergardenor')
def teacher_save(request):
    id = request.GET.get('id')  # User的id

    if id == None:
        form = TeacherForm(request.POST)
    else:
        m = get_object_or_404(User, pk=id)  # user
        form = ChangeTeacherForm(request.POST, instance=m)

    try:
        if form.is_valid():
            with transaction.atomic():
                if id == None:
                    user = User.objects.create_user(form.cleaned_data['username'],
                                                    form.cleaned_data['password'],
                                                    type=User.TEACHER,
                                                    name=form.cleaned_data['name'],
                                                    is_active=form.cleaned_data['is_active'],
                                                    )
                    perms = Permission.objects.filter(codename__in=['manage_teacher'])
                    user.user_permissions.set(perms)
                    instance = Teacher.objects.create(user=user,classes_id=form.cleaned_data['classes'][0])

                    instance.save()
                    BizLog.objects.addnew(request.user, BizLog.INSERT,
                                          u"添加教师[%s],id=%d" % (instance.user.name, instance.user.id))
                else:
                    instance = form.save(commit=False)
                    teacher = instance.bind_teacher
                    teacher.classes_id=int(form.cleaned_data['classes'][0])
                    teacher.save()
                    instance.save()
                    BizLog.objects.addnew(request.user, BizLog.UPDATE,
                                          u"修改教师[%s],id=%d" % (instance.name, instance.id))

            return JSONResponse({'id': instance.id})
        else:
            return JSONError(utils.dump_form_errors(form))
    except Exception, e:
        return JSONError(unicode(e))


@csrf_exempt
@user_passes_test(lambda u: u.is_superuser)
def group_home(request, template_name, extra_context=None):
    form = GroupForm()

    permissions = {}
    #rows = Permission.objects.filter(codename__startswith="manage_")
    rows = Permission.objects.filter()
    for row in rows:
        item = {'id': row.id, 'name': row.name}
        if permissions.has_key(row.content_type.name):
            permissions[row.content_type.name].append(item)
        else:
            permissions[row.content_type.name] = [item, ]

    return render_to_response(template_name, {'form': form, 'permissions': permissions},
                              context_instance=RequestContext(request))


@csrf_exempt
@login_required()
def group_data(request):
    try:
        rows = Group.objects.all()
        result = []
        for row in rows:
            permissions = []
            permission_names = []
            for permission in row.permissions.all():
                permissions.append(str(permission.id))
                permission_names.append(permission.name)

            item = {'id': row.id, 'name': row.name,
                    'permissions': permissions, 'permission_text': ','.join(permission_names), }
            result.append(item)
        return JSONResponse(result)
    except Exception, e:
        return JSONError(str(e))


@csrf_exempt
@user_passes_test(lambda u: u.is_superuser)
def group_save(request):
    id = request.GET.get('id')

    if id == None:
        form = GroupForm(request.POST)
    else:
        group = get_object_or_404(Group, pk=id)
        form = GroupForm(request.POST, instance=group)

    try:
        if form.is_valid():
            group = form.save()
            return JSONResponse({'id': group.id})
        else:
            return JSONError(utils.dump_form_errors(form))
    except Exception, e:
        traceback.print_exc()
        return JSONError(unicode(e))


@csrf_exempt
@user_passes_test(lambda u: u.is_superuser)
def group_delete(request):
    id = request.GET.get('id')
    group = get_object_or_404(Group, pk=id)
    group.delete()
    return JSONResponse({})


@csrf_exempt
@login_required()
def permission_data(request):
    try:
        rows = Permission.objects.all()
        result = []
        for row in rows:
            item = {'id': row.id, 'text': row.name, 'group': row.content_type.name}
            result.append(item)
        return JSONResponse(result)
    except Exception, e:
        return JSONError(str(e))


@csrf_exempt
@login_required()
def kindergarten_data(request):
    try:
        rows = Kindergarten.objects.all()
        result = []
        for row in rows:
            item = {'id':row.id,'name':row.name}
            result.append(item)
        return JSONResponse(result)
    except Exception, e:
        return JSONError(str(e))

@csrf_exempt
def class_data(request):
    if not request.user.has_perm('account.manage_kindergardenor') and not request.user.has_perm('account.manage_teacher'):
        raise PermissionDenied()
    rows = Classes.objects.all()
    if request.user.type == User.KINDERGARTENOR:
        rows = rows.filter(grade__kindergarten=request.user.bind_kindergartenor.kindergarten)
    elif request.user.type == User.TEACHER:
        # teacher = request.user.bind_teacher
        # kindergarten = teacher.classes.grade.kindergarten
        rows = rows.filter(grade__kindergarten=request.user.bind_teacher.classes.grade.kindergarten)
    data = []
    for row in rows:
        info = {}
        info['id'] = row.id
        info['name'] = row.name
        data.append(info)
    return JSONResponse(data)