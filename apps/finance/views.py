# coding=utf8
import tablib
import traceback

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test, PermissionDenied
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from libs.http import JSONResponse, JSONError, DataGridJSONResponse
from apps.system.models import BizLog
from apps.finance.froms import *
# from apps.account.models import UserPromoting
# from apps.order.models import Order

# 财务流水
@permission_required('finance.view_journals')
def journal(request, template_name, extra_context=None):
    return render_to_response(template_name, {'Journals': Journals}, context_instance=RequestContext(request))


@csrf_exempt
@permission_required('finance.view_journals')
def journal_data(request):
    rows = Journals.objects.all()

    q = request.POST.get('q')
    keyword = request.POST.get('keyword')
    date_begin = request.POST.get('date_begin')
    date_end = request.POST.get('date_end')
    type = request.POST.get('type')
    export = request.POST.get('export')

    if keyword and len(keyword):
        if q == "username":
            rows = rows.filter(create_user__username__icontains=keyword)
        elif q == "order_no":
            rows = rows.filter(order__no__icontains=keyword)

    if type and len(type):
        rows = rows.filter(type=type)
    if date_begin and len(date_begin):
        rows = rows.filter(create_time__gte=date_begin)
    if date_end and len(date_end):
        rows = rows.filter(create_time__lte=date_end+' 23:59:59')

    if export:
        headers = (u'用户', u'类别', u'金额', u'余额', u'描述', u'备注', u'时间')
        data = []
        for row in rows:
            d = row.to_dict()
            data.append(
                (
                    d['create_user_text'],
                    d['type_text'],
                    d['total_fee'],
                    d['balance'],
                    d['description'],
                    d['notes'],
                    d['create_time'],
                )
            )

        data = tablib.Dataset(*data, headers=headers, title=u"数据")

        filename = settings.TMP_ROOT + "/export.xlsx"
        open(filename, 'wb').write(data.xlsx)

        response = HttpResponse(utils.read_file(filename), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=财务流水.xlsx'
        BizLog.objects.addnew(request.user, BizLog.EXPORT, u"导出财务流水数据")
        return response
    else:
        rows, total = utils.get_page_data(request, rows)

        data = []
        for row in rows:
            data.append(row.to_dict())
        dict = {"total": total, "rows": data}
        return JSONResponse(dict)

# 账单
@permission_required('finance.view_bill')
def bill(request, template_name, extra_context=None):
    return render_to_response(template_name, {'Bill': Bill, 'Order':Order}, context_instance=RequestContext(request))


@csrf_exempt
@permission_required('finance.view_bill')
def bill_data(request):
    rows = Bill.objects.all()

    q = request.POST.get('q')
    keyword = request.POST.get('keyword')
    date_begin = request.POST.get('date_begin')
    date_end = request.POST.get('date_end')
    order_type = request.POST.get('type')
    pay_mode = request.POST.get('pay_mode')
    export = request.POST.get('export')

    if keyword and len(keyword):
        if q == "username":
            rows = rows.filter(user__username__icontains=keyword)
        elif q == "order_no":
            rows = rows.filter(order__no__icontains=keyword)

    if order_type and len(order_type):
        rows = rows.filter(order__type=order_type)
    if pay_mode and len(pay_mode):
        rows = rows.filter(pay_mode=pay_mode)
    if date_begin and len(date_begin):
        rows = rows.filter(pay_time__gte=date_begin)
    if date_end and len(date_end):
        rows = rows.filter(pay_time__lte=date_end+' 23:59:59')

    if export:
        headers = (u'用户', u'订单号', u'订单类别', u'下单时间', u'金额', u'支付方式', u'支付时间', u'交易号', u'支付账号')
        data = []
        for row in rows:
            d = row.to_dict()
            data.append(
                (
                    d['user_text'],
                    d['order_no'],
                    d['order_type_text'],
                    d['order_create_time'],
                    d['totalfee'],
                    d['pay_mode_text'],
                    d['pay_time'],
                    d['tradeno'],
                    d['buyer'],
                )
            )

        data = tablib.Dataset(*data, headers=headers, title=u"数据")

        filename = settings.TMP_ROOT + "/export.xlsx"
        open(filename, 'wb').write(data.xlsx)

        response = HttpResponse(utils.read_file(filename), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=账单记录.xlsx'
        BizLog.objects.addnew(request.user, BizLog.EXPORT, u"导出账单记录数据")
        return response
    else:
        rows, total = utils.get_page_data(request, rows)

        data = []
        for row in rows:
            data.append(row.to_dict())
        dict = {"total": total, "rows": data}
        return JSONResponse(dict)

def check_promoting_perm(user):
    if not user.has_perm('finance.view_promoting') and not user.is_teacher():
        raise PermissionDenied()

    return user.is_teacher()

#@permission_required('finance.view_promoting')
def promoting(request, template_name, extra_context=None):
    check_promoting_perm(request.user)
    return render_to_response(template_name, {}, context_instance=RequestContext(request))


@csrf_exempt
#@permission_required('finance.view_promoting')
def promoting_data(request):
    check_promoting_perm(request.user)
    rows = UserPromoting.objects.all()
    if request.user.is_teacher():
        rows = rows.filter(src_user=request.user)

    q = request.POST.get('q')
    keyword = request.POST.get('keyword')

    if q == "username":
        rows = rows.filter(create_user__username=keyword)

    elif q == 'type_text':
        rows = rows.filter(type=keyword)

    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        data.append(row.to_dict())
    dict = {"total": total, "rows": data}
    return JSONResponse(dict)


@login_required()
def income(request, template_name, extra_context=None):
    return render_to_response(template_name, {}, context_instance=RequestContext(request))


@csrf_exempt
@login_required()
def income_data(request):
    rows = Income.objects.filter(user=request.user)

    q = request.POST.get('q')
    keyword = request.POST.get('keyword')

    if q == "username":
        rows = rows.filter(create_user__username=keyword)

    elif q == 'type_text':
        rows = rows.filter(type=keyword)

    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        data.append(row.to_dict())
    dict = {"total": total, "rows": data}
    return JSONResponse(dict)

@login_required()
def drawing_account(request, template_name, extra_context=None):
    if not request.user.is_teacher():
        raise PermissionDenied()

    return render_to_response(template_name, {
        'DrawingAccount':DrawingAccount,
        'form':DrawingAccountForm()
    }, context_instance=RequestContext(request))


@csrf_exempt
@login_required()
def drawing_account_data(request):
    if not request.user.is_teacher():
        raise PermissionDenied()

    rows = DrawingAccount.objects.all()

    q = request.POST.get('q')
    keyword = request.POST.get('keyword')
    type = request.GET.get('type')

    if q == "username":
        rows = rows.filter(create_user__username=keyword)
    elif q == 'type_text':
        rows = rows.filter(type=keyword)

    if type and len(type) > 0:
        rows = rows.filter(type=type)

    if request.user.is_teacher():
        rows = rows.filter(create_user=request.user)

    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        data.append(row.to_dict())
    dict = {"total": total, "rows": data}
    return JSONResponse(dict)


@csrf_exempt
@login_required()
def drawing_account_save(request):
    id = request.GET.get('id')
    if id == None:
        form = DrawingAccountForm(request.POST)
    else:
        m = get_object_or_404(DrawingAccount, pk=id)
        form = DrawingAccountForm(request.POST, instance=m)

    try:
        if form.is_valid():
            with transaction.atomic():
                instance = form.save(request=request)

                if id == None:
                    BizLog.objects.addnew(request.user, BizLog.INSERT, u"添加提现账号[%s],id=%d" % (instance.account_number, instance.id))
                else:
                    BizLog.objects.addnew(request.user, BizLog.UPDATE, u"修改提现账号[%s],id=%d" % (instance.account_number, instance.id))

            return JSONResponse({'id': instance.id})
        else:
            return JSONError(utils.dump_form_errors(form))
    except Exception, e:
        return JSONError(unicode(e))


@csrf_exempt
@login_required()
def drawing_account_delete(request):
    id = request.GET.get('id')
    instance = get_object_or_404(DrawingAccount, pk=id)
    with transaction.atomic():
        BizLog.objects.addnew(request.user, BizLog.INSERT, u"删除提现账号[%s],id=%d" % (instance.account_number, instance.id))
        instance.delete()
    return JSONResponse({})

def check_perm(user):
    if not user.has_perm('finance.view_drawing') and not user.is_teacher():
        raise PermissionDenied()

# 提现记录
@login_required()
def drawing_record(request, template_name, extra_context=None):
    check_perm(request.user)

    drawing = Drawing.objects.all()
    return render_to_response(template_name, {'drawing': drawing}, context_instance=RequestContext(request))


@csrf_exempt
@login_required()
def drawing_record_data(request):
    check_perm(request.user)

    rows = Drawing.objects.all()
    if request.user.is_teacher():
        rows = rows.filter(create_user=request.user)

    q = request.POST.get('q')
    keyword = request.POST.get('keyword')

    if q == "order_no":
        rows = rows.filter(no=keyword)

    elif q == 'status':
        rows = rows.filter(status=keyword)

    elif q == 'username':
        rows = rows.filter(create_user__username=keyword)
    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        data.append(row.to_dict())
    dict = {"total": total, "rows": data}
    return JSONResponse(dict)


@csrf_exempt
@permission_required('finance.check_drawing')
def drawing_record_accept(request):
    pk = request.GET.get('id')
    status = int(request.GET.get('status'))
    notes = request.GET.get('notes')

    try:
        with transaction.atomic():
            drawing = get_object_or_404(Drawing, pk=int(pk))
            drawing.status = status
            drawing.notes = notes

            DrawingStatus.objects.create(main=drawing, status=status, create_user=request.user)

            if status == Drawing.PENDING:
                status_text = u'提现中'
            elif status == Drawing.FINISHED:
                status_text = u'已完成'
                if drawing.total_fee > drawing.create_user.balance:
                    raise Exception(u'余额不足，无法完成操作！')

                drawing.create_user.balance -= drawing.total_fee
                drawing.create_user.save()
                drawing.balance_after = drawing.create_user.balance
            else:
                status_text = u'拒绝'
            drawing.save()
            BizLog.objects.addnew(request.user, BizLog.UPDATE, u"%s[%s],id=%d" % (status_text, drawing.no, drawing.id))
        return JSONResponse({})
    except Exception, e:
        return JSONError(unicode(e))


# 提现申请
@csrf_exempt
@login_required()
def drawing_withdraw(request, template_name, extra_context=None):
    if request.method == 'POST':
        form = DrawingForm(request.POST)
        if form.is_valid():
            total_fee = int(form.cleaned_data['total_fee'])
            balance_before = request.user.balance
            type = form.cleaned_data['type']
            account_number = form.cleaned_data['account_number']
            account_name = form.cleaned_data['account_name']
            account_bank = form.cleaned_data['account_bank']
            status = 0
            if total_fee <= balance_before:
                Drawing.objects.create(
                    total_fee=total_fee,
                    type=type,
                    balance_before=balance_before,
                    account_bank=account_bank,
                    account_number=account_number,
                    account_name=account_name,
                    status=status,
                    create_user=request.user
                )

                return render_to_response(template_name, {'success': 'true', 'form': form},
                                          context_instance=RequestContext(request))
            else:
                return render_to_response(template_name, {'success':'false', 'msg': '提现金额不能大于您的余额', 'form': form})
    else:
        form = DrawingForm()
    return render_to_response(template_name, {'form': form}, context_instance=RequestContext(request))

@permission_required('finance.mange_commissionratio')
def commission_ratio_home(request, template_name, extra_context=None):
    form = CommissionRatioForm()
    return render_to_response(template_name, {'form': form}, context_instance=RequestContext(request))

@csrf_exempt
@permission_required('finance.mange_commissionratio')
def commission_ratio_list(request):
    rows = CommissionRatio.objects.filter()
    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        data.append(row.to_dict())
    return DataGridJSONResponse(data, total)


@csrf_exempt
@permission_required('finance.mange_commissionratio')
def commission_ratio_save(request):
    id = request.GET.get('id')

    try:
        if id == None:
            form = CommissionRatioForm(request.POST)
        else:
            instance = get_object_or_404(CommissionRatio, pk=id)
            form = CommissionRatioForm(request.POST, instance=instance)

        if form.is_valid():
            if id == None:
                CommissionRatio.objects.filter(type=form.cleaned_data['type']).delete()

            cr = form.save()

            if id == None:
                BizLog.objects.addnew(request.user, BizLog.INSERT,
                                      u"添加分成比例[%s],id=%d" % (cr.get_type_display(), cr.id), cr.to_dict())
            else:
                BizLog.objects.addnew(request.user, BizLog.UPDATE,
                                      u"修改分成比例[%s],id=%d" % (cr.get_type_display(), cr.id), cr.to_dict())

            return JSONResponse({"data": cr.id})
        else:
            return JSONError(utils.dump_form_errors(form))
    except Exception, e:
        traceback.print_exc()
        return JSONError(u'保存失败！')


@permission_required('finance.mange_commissionratio')
def commission_ratio_delete(request):
    id = request.GET.get('id')
    try:
        cr = get_object_or_404(CommissionRatio, pk=int(id))
        BizLog.objects.addnew(request.user, BizLog.DELETE,
                              u"删除分成比例[%s],id=%d" % (cr.name, cr.id), cr.to_dict())
        cr.delete()
    except Exception:
        traceback.print_exc()
        return JSONError(u'删除失败！')

    return JSONResponse({})