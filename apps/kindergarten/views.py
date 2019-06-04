# coding:utf-8
import traceback

import tablib
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.db import transaction
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import permission_required

from apps.classes.forms import KindergartenForm
from apps.system.models import BizLog
from libs import utils
from libs.http import JSONResponse, JSONError
from models import *
from forms import *
@csrf_exempt
@permission_required('account.manage_company')
def kindergarten_list(request, template_name, extra_context=None):
    form = KindergartenForm()
    return render_to_response(template_name,{'form': form},context_instance=RequestContext(request))


@csrf_exempt
@permission_required('account.manage_company')
def kindergarten_data(request):
    """幼儿园数据"""
    q = request.POST.get('q')
    keyword = request.POST.get('keyword')

    rows = Kindergarten.objects.all()

    if keyword and len(keyword)>0:
        if q == 'status':
            rows = rows.filter(status=keyword)
        elif q == 'kindergarten_name':
            rows = rows.filter(name__icontains=keyword)
        elif q == 'ID':
            rows = rows.filter(account_book=keyword)
    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        item = row.to_dict()
        data.append(item)

    dict = {"total": total, "rows": data}
    return JSONResponse(dict)


@csrf_exempt
@permission_required('account.manage_company')
def kindergarten_save(request):
    """保存幼儿园信息"""
    id = request.GET.get('id')
    if id == None:
        form = KindergartenForm(request.POST)
    else:
        kindergarten = get_object_or_404(Kindergarten, pk=id)
        form = KindergartenForm(request.POST, instance=kindergarten)
    try:
        if form.is_valid():
            with transaction.atomic():
                if id == None:
                    kindergarten = form.save()
                else:
                    form.save()
                if id == None:
                    BizLog.objects.addnew(request.user, BizLog.INSERT, u"添加幼儿园[%s],id=%d" % (kindergarten.name, kindergarten.id),
                                          kindergarten.to_dict())
                else:
                    BizLog.objects.addnew(request.user, BizLog.UPDATE, u"修改幼儿园[%s],id=%d" % (kindergarten.name, kindergarten.id),
                                          kindergarten.to_dict())

            return JSONResponse({'id': kindergarten.id})
        else:
            return JSONError(utils.dump_form_errors(form))
    except Exception, e:
        traceback.print_exc()
        return JSONError(unicode(e))

@csrf_exempt
@permission_required('account.manage_company')
def subject_list(request, template_name, extra_context=None):
    form = SubjectForm()
    return render_to_response(template_name, context={'form':form},context_instance=RequestContext(request))

@csrf_exempt
@permission_required('account.manage_kindergardenor')
def icome_list(request, template_name, extra_context=None):
    form = IcomForm()
    sub = Subject.objects.filter(type=Subject.ICOME)  # 可按科目进行查询
    return render_to_response(template_name, context={'form':form,'sub':sub},context_instance=RequestContext(request))

@csrf_exempt
@permission_required('account.manage_kindergardenor')
def expense_list(request, template_name, extra_context=None):
    form = ExpenseForm()
    sub = Subject.objects.filter(type=Subject.EXPENSE)
    return render_to_response(template_name, context={'form':form,'sub':sub},context_instance=RequestContext(request))


@csrf_exempt
@permission_required('account.manage_company')
def subject_data(request):
    q = request.POST.get('q')
    keyword = request.POST.get('keyword')
    rows = Subject.objects.all()
    if q == 'type':
        rows = rows.filter(type=keyword)
    elif q == 'code':
        rows = rows.filter(code=keyword)
    rows,total = utils.get_page_data(request,rows)

    data = []
    for row in rows:
        item = row.to_dict()
        data.append(item)

    dict = {"total": total, "rows": data}
    return JSONResponse(dict)


@csrf_exempt
@permission_required('account.manage_kindergardenor')
def expense_data(request):
    q = request.POST.get('q')
    keyword = request.POST.get('keyword')
    export = request.POST.get('export')
    date_begin = request.POST.get('date_begin')
    date_end = request.POST.get('date_end')
    sub = request.POST.get('sub')  # 导出数据获取科目字段
    rows = Expense.objects.filter(kindergarten=request.user.bind_kindergartenor.kindergarten)  # 园长下
    if date_begin:
        rows = rows.filter(create_time__gte=date_begin)
    if date_end:
        rows = rows.filter(create_time__lte=date_end)
    if sub:
        rows = rows.filter(code=sub)
    if keyword and len(keyword) > 0:
        if q == 'sub':
            rows = rows.filter(code=keyword)
        elif q == 'code':
            rows = rows.filter(code__code=keyword)

    if export:
        headers = (u'备注', u'金额', u'科目', u'科目编码', u'时间', u'提交人')

        rows = rows.values('notes','balance','code__name','code__code','create_time','submitter__name')

        data = []
        for row in rows:#使导出的xlsx文件格式规范不出现编号，null等字符串
            if row['notes'] is None:
                row['notes'] = u'无'
            if row['balance'] is None:
                row['balance'] = u'无'
            if row['code__name'] is None:
                row['code__name'] = u'无'
            if row['code__code'] is None:
                row['code__code'] = u'无'
            if row['create_time'] is None:
                row['create_time'] = u'无'
            if row['submitter__name'] is None:
                row['submitter__name'] = u'无'

            data.append(
                (
                    row['notes']+' ',
                    row['balance'],
                    row['code__name'],
                    row['code__code'],
                    row['create_time'],
                    row['submitter__name'],
                )
            )

        data = tablib.Dataset(*data, headers=headers, title=u"数据")


        filename = settings.TMP_ROOT + "/export_member.xlsx"
        open(filename, 'wb').write(data.xlsx)

        response = HttpResponse(utils.read_file(filename), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=支出表.xlsx'
        BizLog.objects.addnew(request.user, BizLog.EXPORT, u"导出支出数据")
        return response
    else:
        rows,total = utils.get_page_data(request,rows)

    data = []
    for row in rows:
        item = row.to_dict()
        data.append(item)

    dict = {"total": total, "rows": data}
    return JSONResponse(dict)


@csrf_exempt
@permission_required('account.manage_kindergardenor')
def expense_save(request):
    form = ExpenseForm(request.POST)
    try:
        if form.is_valid():
            with transaction.atomic():
                sub = form.save(commit=False)
                sub.kindergarten = request.user.bind_kindergartenor.kindergarten
                sub.submitter = request.user
                sub.save()
                BizLog.objects.addnew(request.user, BizLog.INSERT, u"添加支出[%s],id=%d" % (sub.notes, sub.id),
                                          sub.to_dict())
            return JSONResponse({'id': sub.id})
        else:
            return JSONError(utils.dump_form_errors(form))
    except Exception, e:
        traceback.print_exc()
        return JSONError(unicode(e))


@csrf_exempt
@permission_required('account.manage_kindergardenor')
def icome_data(request):
    q = request.POST.get('q')
    keyword = request.POST.get('keyword')
    export = request.POST.get('export')
    date_begin = request.POST.get('date_begin')
    sub = request.POST.get('sub')  # 导出数据获取科目字段
    date_end = request.POST.get('date_end')
    rows = Icome.objects.filter(kindergarten=request.user.bind_kindergartenor.kindergarten)
    if date_begin:
        rows = rows.filter(create_time__gte=date_begin)
    if date_end:
        rows = rows.filter(create_time__lte=date_end)
    if sub:
        rows = rows.filter(code=sub)
    if keyword and len(keyword) > 0:
        if q == 'sub':
            rows = rows.filter(code=keyword)
        elif q == 'code':
            rows = rows.filter(code__code=keyword)

    if export:
        headers = (u'备注', u'金额', u'科目', u'科目编码', u'时间', u'提交人')

        rows = rows.values('notes','balance','code__name','code__code','create_time','submitter__name')

        data = []
        for row in rows:#使导出的xlsx文件格式规范不出现编号，null等字符串
            if row['notes'] is None:
                row['notes'] = u'无'
            if row['balance'] is None:
                row['balance'] = u'无'
            if row['code__name'] is None:
                row['code__name'] = u'无'
            if row['code__code'] is None:
                row['code__code'] = u'无'
            if row['create_time'] is None:
                row['create_time'] = u'无'
            if row['submitter__name'] is None:
                row['submitter__name'] = u'无'

            data.append(
                (
                    row['notes']+' ',
                    row['balance'],
                    row['code__name'],
                    row['code__code'],
                    row['create_time'],
                    row['submitter__name'],
                )
            )

        data = tablib.Dataset(*data, headers=headers, title=u"数据")


        filename = settings.TMP_ROOT + "/export_member.xlsx"
        open(filename, 'wb').write(data.xlsx)

        response = HttpResponse(utils.read_file(filename), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=收入表.xlsx'
        BizLog.objects.addnew(request.user, BizLog.EXPORT, u"导出收入数据")
        return response
    else:
        rows,total = utils.get_page_data(request,rows)

    data = []
    for row in rows:
        item = row.to_dict()
        data.append(item)

    dict = {"total": total, "rows": data}
    return JSONResponse(dict)


@csrf_exempt
@permission_required('account.manage_kindergardenor')
def icome_save(request):
    form = IcomForm(request.POST)
    try:
        if form.is_valid():
            with transaction.atomic():
                sub = form.save(commit=False)
                sub.kindergarten = request.user.bind_kindergartenor.kindergarten
                sub.submitter = request.user
                sub.save()
                BizLog.objects.addnew(request.user, BizLog.INSERT, u"添加收入[%s],id=%d" % (sub.notes, sub.id),
                                          sub.to_dict())
            return JSONResponse({'id': sub.id})
        else:
            return JSONError(utils.dump_form_errors(form))
    except Exception, e:
        traceback.print_exc()
        return JSONError(unicode(e))


@csrf_exempt
@permission_required('account.manage_company')
def subject_save(request):
    id = request.GET.get('id')
    if id == None:
        form = SubjectForm(request.POST)
    else:
        sub = get_object_or_404(Subject, pk=id)
        form = SubjectForm(request.POST, instance=sub)

    try:
        if form.is_valid():
            with transaction.atomic():
                sub = form.save()
                if id == None:
                    BizLog.objects.addnew(request.user, BizLog.INSERT, u"添加科目[%s],id=%d" % (sub.name, sub.id),
                                          sub.to_dict())
                else:
                    BizLog.objects.addnew(request.user, BizLog.UPDATE, u"修改科目[%s],id=%d" % (sub.name, sub.id),
                                          sub.to_dict())
            return JSONResponse({'id': sub.id})
        else:
            return JSONError(utils.dump_form_errors(form))
    except Exception, e:
        traceback.print_exc()
        return JSONError(unicode(e))