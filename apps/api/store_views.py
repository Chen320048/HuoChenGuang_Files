# coding=utf-8

import json
import traceback

from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from libs.http import JSONResponse, JSONError
from libs import utils
from apps.account.decorators import token_required
from apps.store.models import Product, Category, Cart
from apps.account.models import MemberFootMark, MemberCollection
from apps.api import check_user

def store_product_category_list(request):
    id = request.GET.get('id',0)
    rows = Category.objects.filter(level=Category.LEVEL_0)
    # 如果客户端上传了父id，则返回二级类型
    if int(id) > 0:
        rows = Category.objects.filter(parent=id)

    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        item = row.to_dict()
        data.append(item)

    return JSONResponse({'data': data})

def store_product_sub_category_list(request,id):
    rows = Category.objects.filter(level=Category.LEVEL_0)

    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        item = row.to_dict()
        data.append(item)

    return JSONResponse({'data': data})

def store_product_list(request):
    grade = request.GET.get('grade')
    subject = request.GET.get('subject')    #商品子类，不是年级科目
    category = request.GET.get('category')
    orderby = request.GET.get('orderby', '-id') # 排序字段：id、guide_price、sales

    rows = Product.objects.filter().order_by(orderby).exclude(remove_time__isnull=False)

    if grade:
        rows = rows.filter(grade_id=grade)
    if subject:
        rows = rows.filter(subcategory_id=subject)
    if category:
        rows = rows.filter(category_id=category)

    rows, total = utils.get_page_data(request, rows)

    user = check_user(request)
    data = []
    for row in rows:
        item = row.to_api_dict()
        item['discount_price'] = row.get_discount_price(user)
        data.append(item)

    return JSONResponse({'data': data})


def store_product_detail(request, id):
    product = Product.objects.get(pk=id)

    data = product.to_detail_dict()

    user = check_user(request)
    if user:
        MemberFootMark.objects.create(type=MemberFootMark.PRODUCT, object_id=id, create_user=user)

    data['collected'] = 0
    if user:
        data['discount_price'] = product.get_discount_price(user)

        mc = MemberCollection.objects.filter(type=MemberCollection.PRODUCT, object_id=id, create_user=user).first()
        if mc:
            data['collected'] = mc.id
    else:
        data['discount_price'] = product.guide_price

    return JSONResponse({'data': data})

@token_required
def store_cart(request, user):
    rows = Cart.objects.filter(create_user=user)

    data = []
    for row in rows:
        item = row.to_dict()
        data.append(item)

    return JSONResponse({'data': data})

@token_required
def store_cart_num(request, user):
    nums = Cart.objects.filter(create_user=user).count()

    return JSONResponse({'data': {'nums':nums}})

@csrf_exempt
@token_required
def store_cart_add(request, user):
    params = json.loads(request.body)
    try:
        product_id = params['product_id']
        quantily = params['quantily']
    except KeyError:
        return JSONError(u'参数无效！')

    try:
        cart = Cart.objects.filter(product_id = product_id, create_user = user).first()
        if cart:
            cart.quantily += quantily
            cart.save()
        else:
            Cart.objects.create(
                product_id = product_id,
                quantily = quantily,
                create_user = user
            )

        return JSONResponse({'data': {}})
    except Exception:
        traceback.print_exc()
        return JSONError(u'添加失败！')

@csrf_exempt
@token_required
def store_cart_remove(request, user):
    params = json.loads(request.body)
    try:
        product_ids = params['product_ids']
    except KeyError:
        return JSONError(u'参数无效！')

    try:
        product_ids = product_ids.split(',')
        for id in product_ids:
            Cart.objects.filter(
                product_id = id,
                create_user = user
            ).delete()

        return JSONResponse({'data': {}})
    except Exception:
        traceback.print_exc()
        return JSONError(u'移除失败！')

@token_required
def store_cart_clear(request, user):
    try:
        Cart.objects.filter(
            create_user = user
        ).delete()

        return JSONResponse({'data': {}})
    except Exception:
        traceback.print_exc()
        return JSONError(u'移除失败！')

@csrf_exempt
@token_required
def store_cart_update(request, user):
    params = json.loads(request.body)
    try:
        product_id = params['product_id']
        quantily = params['quantily']
    except KeyError:
        return JSONError(u'参数无效！')

    try:
        Cart.objects.filter(
            product_id = product_id,
            create_user = user
        ).update(
            quantily=quantily
        )

        return JSONResponse({'data': {}})
    except Exception:
        traceback.print_exc()
        return JSONError(u'更新失败！')