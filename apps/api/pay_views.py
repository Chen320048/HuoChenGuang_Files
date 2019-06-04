# coding=utf-8

import json
import traceback

from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.utils import timezone
from django.db import transaction
from django.http import HttpResponse
from django.db.models import Q, F

from libs.alipay import alipay as libs_alipay
from libs.http import JSONResponse, JSONError
from libs import utils
from apps.account.decorators import token_required
from libs.pay import pay
from apps.account.models import Member, UserPromoting
from apps.order.models import Order, Notify
from apps.finance.models import Bill, IAP, handle_pay


from alipay import AliPay
from libs.weixinpay.weixinpay import weixinpay_call_back

@csrf_exempt
def via_alipay_notify(request):
    """
    参考文档：https://docs.open.alipay.com/204/105301/
    """

    try:
        args = request.POST

        print args

        notify_type = request.POST.get('notify_type')
        if not notify_type == 'trade_status_sync':
            return HttpResponse('fail')

        # 判断交易类型,如果是TRADE_CLOSED或TRADE_SUCCESS进行处理,分别是退款和付款成功,其它的直接返回success
        trade_status = request.POST.get('trade_status')

        # 业务相关信息
        order_no = request.POST.get('out_trade_no')
        trade_no = request.POST.get('trade_no')

        if trade_status == 'TRADE_SUCCESS':
            check_sign = libs_alipay.alipay_core.params_to_query(args)
            params = libs_alipay.alipay_core.query_to_dict(check_sign)
            sign = params['sign']
            params = libs_alipay.alipay_core.params_filter(params)
            message = libs_alipay.alipay_core.params_to_query(params, quotes=False, reverse=False)

            # 验证平台签名
            check_res = libs_alipay.alipay_core.check_ali_sign(message, sign)
            # check_res = alipay.alipay_core.check_sign(message,sign)
            if check_res is False:
                print('check_wrong')
                return HttpResponse('fail')
            # 验证回调信息真实性
            res = libs_alipay.alipay_core.verify_from_gateway(
                {'partner': libs_alipay.alipay_config.PID, 'notify_id': params['notify_id']})
            if res is False:
                print('gateway_wrong')
                return HttpResponse('fail')

            # data = request.POST.dict()
            # signature = data.pop("sign")
            # alipay = get_alipay()
            # success = alipay.verify(data, signature)

            print '\r\nPASS\r\n'

            # 付款完成业务逻辑处理
            buyer_email = request.POST.get('buyer_logon_id')
            total_fee = float(request.POST.get('total_amount'))
            pay_time = request.POST.get('gmt_payment')

            order = Order.objects.get(no=order_no)

            # 已付款,不允许重新付款
            if order.status >= Order.STATUS_PAYED:
                return HttpResponse('failure')

            with transaction.atomic():
                order.status = order.STATUS_PAYED
                order.pay_mode = Order.ALIPAY
                handle_pay(order,  Order.ALIPAY, total_fee)
                Bill.objects.create(
                    user=order.create_user,
                    pay_mode=Bill.ALIPAY,
                    pay_time=pay_time,
                    tradeno=trade_no,
                    buyer=buyer_email,
                    totalfee=total_fee,
                    order=order,
                    alert=False
                )
            return HttpResponse('success')
        else:
            return HttpResponse('success')
    except Exception, e:
        traceback.print_exc()
        return HttpResponse('fail')


@csrf_exempt
def via_wxpay_notify(request):
    print '=============>Receive WeinxinPay Notify:'
    try:
        res = pay.handle_wxnotify(request)
        if not res:
            HttpResponse('failure')
        print res
        if res['return_code'] == "SUCCESS":
            order_no = res['out_trade_no']
            trade_no = res['transaction_id']
            buyer_email = res['openid']
            total_fee = round(float(res['total_fee'])/100, 2)
            pay_time = res['time_end']
            pay_time = pay_time[:4] + '-' + pay_time[4:6] + '-' + pay_time[6:8] + ' ' + pay_time[8:10] + ':' + pay_time[10:12] + ':' + pay_time[12:]
            with transaction.atomic():
                order = Order.objects.get(no=order_no)
                with transaction.atomic():
                    order.status = Order.STATUS_FINISHEED
                    order.pay_mode = Order.WEIXIN
                    handle_pay(order,  Order.WEIXIN, res['total_fee'])
                    Bill.objects.create(
                        order=order,
                        user=order.create_user,
                        pay_mode=Bill.WEIXIN,
                        pay_time=pay_time,
                        tradeno=trade_no,
                        buyer=buyer_email,
                        totalfee=total_fee,
                        alert=False
                    )
                return HttpResponse(
                    """<xml>
                    <return_code><![CDATA[SUCCESS]]></return_code>
                    <return_msg><![CDATA[OK]]></return_msg>
                    </xml>""",
                    content_type="application/xml"
                )
    except Exception, e:
        traceback.print_exc()

    return HttpResponse('failure')


@csrf_exempt
@token_required
def alipay_create(request, user):
    try:
        p = json.loads(request.body)

        out_trade_no = p['out_trade_no']
        total_fee = float(p['total_fee'])

        order = Order.objects.get(no=out_trade_no)

        if total_fee != order.total_fee:
           return JSONError(u'金额有误!')

        alipay = pay.get_alipay()
        res = alipay.api_alipay_trade_app_pay((u'支付订单[%s]' % (order.no)).encode("utf8"), out_trade_no, total_amount=total_fee)

        return JSONResponse({'data': res})
    except Order.DoesNotExist:
        return JSONError(u'订单不存在！')
    except Exception, e:
        traceback.print_exc()
        return JSONError(e.message)


@csrf_exempt
@token_required
def wxpay_create(request, user):
    try:
        p = json.loads(request.body)
        #print '------>WeiPay params:', p

        out_trade_no = p['out_trade_no']
        total_fee = int(float(p['total_fee'])*100) # 微信支付单位为分

        order = Order.objects.get(no=out_trade_no)
        if total_fee != order.total_fee*100:
           return JSONError(u'金额有误!')

        res = pay.get_weixinpay(out_trade_no, total_fee)
        #print res
        if not 'prepayid' in res:
            return JSONError(u"发起支付失败")
        else:
            return JSONResponse({'data': res})
    except Order.DoesNotExist:
        return JSONError(u'订单不存在！')
    except Exception, e:
        traceback.print_exc()
        return JSONError(e.message)


@csrf_exempt
@token_required
def balance_pay(request, user):
    # 权限判断
    try:
        p = json.loads(request.body)

        out_trade_no = p['out_trade_no']
        total_fee = float(p['total_fee'])

        orders = Order.objects.filter(no=out_trade_no)
        if orders.count() != 1:
            return JSONError("有重复订单")

        balance  = user.balance
        order = orders[0]

        if total_fee != order.total_fee:
           return JSONError('金额有误!')
        if balance < order.total_fee:
            return JSONError('余额不足!')

        order.pay_mode = Order.BALANCE
        handle_pay(order ,Order.BALANCE, total_fee)
        return JSONResponse({})
    except Exception, e:
        traceback.print_exc()
        return JSONError(e.message)

@csrf_exempt
@token_required
def iap_finish(request, user):
    # 苹果内购验证
    try:
        p = json.loads(request.body)

        order_no = p['order_no']
        total_fee = float(p['total_fee'])
        product_identifier = p['product_identifier']
        receipt = p['receipt']

        orders = Order.objects.filter(no=order_no)
        if orders.count() != 1:
            return JSONError("有重复订单")

        order = orders[0]

        if total_fee != order.total_fee:
           return JSONError('金额有误!')

        iap = IAP.objects.create(
            order=order,
            product_identifier=product_identifier,
            receipt=receipt,
            totalfee=total_fee
        )
        iap.validate()

        return JSONResponse({})
    except Exception, e:
        traceback.print_exc()
        return JSONError(e.message)


