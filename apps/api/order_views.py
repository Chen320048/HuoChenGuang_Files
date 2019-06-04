# coding=utf-8

import json
import base64
import traceback

#from alipay.exceptions import AliPayValidationError
from django.db.models import Q, Count
from django.db import transaction
from django.utils import timezone
from django.conf import settings

from libs.pay import pay
from libs.utils import strftime
from pay_views import *

from apps.order.models import Order, Store, StoreLine, Notify
from apps.store.models import Cart

def _save_image(path, data):
    if data and data != '':
        filename = "%s%s.%s" % (path, timezone.now().strftime('%Y%m%d%H%M%S%f'), 'jpg')
        full_filename = "%s/%s" % (settings.MEDIA_ROOT, filename)
        f = open(full_filename, 'wb')
        f.write(base64.b64decode(data))
        f.close()
        return filename
    else:
        return None

@csrf_exempt
@token_required
def order_price(request, user, type):
    iap = request.GET.get('iap')
    if user.bind_member == None:
        return JSONError(u'非会员账号！')
    # if user.bind_member.level == None:
    #     return JSONError(u'非VIP会员！')

    iap_id = None
    if type == 'teach':
        if not user.bind_member.is_vip():
            if iap == 'true':
                price = settings.PRICE_TEACH_OF_NORMAL_MEMBER_IAP
                iap_id = settings.PRICE_TEACH_OF_NORMAL_MEMBER_IAP_ID
            else:
                price = settings.PRICE_TEACH_OF_NORMAL_MEMBER
        else:
            if iap == 'true':
                price = user.bind_member.level.teach_value_iap
                iap_id = user.bind_member.level.teach_iap_id
            else:
                price = user.bind_member.level.teach_value
    elif type == 'ask':
        if not user.bind_member.is_vip():
            if iap == 'true':
                price = settings.PRICE_ASK_OF_NORMAL_MEMBER_IAP
                iap_id = settings.PRICE_ASK_OF_NORMAL_MEMBER_IAP_ID
            else:
                price = settings.PRICE_ASK_OF_NORMAL_MEMBER
        else:
            if iap == 'true':
                price = user.bind_member.level.ask_value_iap
                iap_id = user.bind_member.level.ask_iap_id
            else:
                price = user.bind_member.level.ask_value
    else:
        return JSONError(u'无效的请求！')

    data = {'price': price}
    if iap_id:
        data['iap_id'] = iap_id

    return JSONResponse({'data': data})


@csrf_exempt
@token_required
def order_store_save(request, user):
    """
    :param request:
        {
            "lines": [
                {
                    "product": 1,
                    "price": 5,
                    "quantily": 2,
                    "amount":10
                }
            ],
            "consignee": "zhangsan",
            "mobile":"18677886655",
            "address":"aleee",
            "total_fee":10,
            "message":"hello"
        }
    :param user:
    :return:
    """
    params = json.loads(request.body)
    try:
        consignee = params['consignee'].strip()
        mobile = params['mobile'].strip()
        address = params['address'].strip()
        message = params['message'].strip()
        total_fee = float(params['total_fee'])
        lines = params['lines']
    except Exception:
        return JSONError(u'参数无效！')

    # if consignee == '':
    #     return JSONError(u'收货人不能为空！')
    # if mobile == '':
    #     return JSONError(u'电话不能为空！')
    # if address == '':
    #     return JSONError(u'地址不能为空！')

    try:
        with transaction.atomic():
            order = Order.objects.create(
                type = Order.STORE,
                total_fee = total_fee,
                create_user = user,
                status = Order.STATUS_DEFAULT
            )
            store = Store.objects.create(
                order=order,
                mobile=mobile,
                address=address,
                consignee=consignee,
                message=message
            )

            amount = 0
            for line in lines:
                amount += float(line['amount'])

                StoreLine.objects.create(
                    order = order,
                    main = store,
                    product_id = line['product'],
                    quantily = line['quantily'],
                    price = line['price'],
                    amount = line['amount']
                )
                Cart.objects.filter(create_user=user,product_id=line['product']).delete()

            if amount <> total_fee:
                raise ValueError(u'金额错误！')

            return JSONResponse({'data': {'order_no':order.no,'create_time':strftime(order.create_time)}})
    except ValueError, e:
        return JSONError(unicode(e))
    except Exception:
        traceback.print_exc()
        return JSONError(u'下单失败！')

@csrf_exempt
@token_required
def order_recharge_save(request, user):
    """
    :param request:
        {
            "total_fee":10,
        }
    :param user:
    :return:
    """
    params = json.loads(request.body)
    try:
        total_fee = float(params['total_fee'])
    except Exception:
        return JSONError(u'参数无效！')

    if total_fee <= 0:
        return JSONError(u'无效的充值金额！')

    try:
        with transaction.atomic():
            order = Order.objects.create(
                type = Order.RECHARGE,
                total_fee = total_fee,
                create_user = user,
                status = Order.STATUS_DEFAULT
            )
            return JSONResponse({'data': {'order_no':order.no,'create_time':strftime(order.create_time)}})
    except ValueError, e:
        return JSONError(unicode(e))
    except Exception:
        traceback.print_exc()
        return JSONError(u'下单失败！')

@csrf_exempt
@token_required
def order_list(request, user):
    iap = request.GET.get('iap')
    rows = Order.objects.filter(create_user=user).exclude(type__in=[Order.RECHARGE])

    rows, total = utils.get_page_data(request, rows)
    data = []
    iap_id = None
    for row in rows:
        item = row.to_api_dict()
        item['type'] = row.type
        item['type_text'] = row.get_type_display()

        data.append(item)

    return JSONResponse({'data': data})

@csrf_exempt
@token_required
def order_detail(request, user, id):
    order = Order.objects.get(pk=id)

    item = order.to_api_dict()

    return JSONResponse({'data': item})

@csrf_exempt
@token_required
def order_notify_read(request, user, id):
    n = Notify.objects.get(id=id, user=user)
    n.has_read = True
    n.save()
    return JSONResponse({'data': {}})

@csrf_exempt
@token_required
def order_notify_unreadcount(request, user):
    count = Notify.objects.filter(user=user, has_read=False).count()
    return JSONResponse({'data': {'count': count}})

@csrf_exempt
@token_required
def order_notify_list(request, user):
    rows = Notify.objects.filter(user=user)

    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        item = row.to_dict()
        data.append(item)

    return JSONResponse({'data': data})