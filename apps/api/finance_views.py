# coding=utf-8
import traceback
import json

from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from libs.http import JSONResponse, JSONError
from libs import utils
from apps.account.decorators import token_required
from apps.finance.models import Drawing, DrawingAccount, Journals
from apps.account.models import UserPromoting
from apps.system.models import BizLog

@csrf_exempt
@token_required
def drawing_account_save(request, user):
    params = json.loads(request.body)

    try:
        with transaction.atomic():
            DrawingAccount.objects.filter(create_user=user).delete()
            da = DrawingAccount.objects.create(
                type=params['type'],
                account_number=params['account_number'],
                account_name=params['account_name'],
                account_bank=params['account_bank'],
                create_user=user
            )
            BizLog.objects.addnew(user, BizLog.UPDATE, u'修改提现账户', da.to_dict())
    except Exception, e:
        traceback.print_exc()
        return JSONError(u'保存失败')

    return JSONResponse({'data': {}})

@csrf_exempt
@token_required
def drawing_account(request, user):
    try:
        data = DrawingAccount.objects.get(create_user=user).to_dict()

    except DrawingAccount.DoesNotExist:
        data = {
            'id': 0,
            'type': -1,
            'account_bank': "",
            'type_text': "",
            'account_number':"",
            'account_name': "",
            'create_time': "",
            'create_user': "",
            'create_user_text': "",
            'balance': user.balance,
        }

    return JSONResponse({'data':data})

@csrf_exempt
@token_required
def drawing_add(request, user):
    params = json.loads(request.body)
    if user.balance < params['total_fee']:
        return JSONError(u'余额不足！')

    try:
        #with transaction.atomic():
        Drawing.objects.create(
            total_fee=params['total_fee'],
            balance_before=user.balance,
            account_bank=params['account_bank'],
            account_number=params['account_number'],
            account_name=params['account_name'],
            type=params['type'],
            create_user=user
        )
    except Exception, e:
        traceback.print_exc()
        return JSONError(u'提现失败')

    return JSONResponse({'data':{}})

@csrf_exempt
@token_required
def drawing_list(request, user):
    rows = Drawing.objects.filter(create_user=user)
    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        item = row.to_dict()
        data.append(item)

    return JSONResponse({'data':data})

@csrf_exempt
@token_required
def journals_list(request, user):
    rows = Journals.objects.filter(create_user=user)
    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        item = row.to_dict()
        data.append(item)

    return JSONResponse({'data':data})