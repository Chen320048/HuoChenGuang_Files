# coding=utf-8

import json
import os
import traceback
import qrcode
import time
import operator

from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from django.template import RequestContext
from django.conf import settings
from django.shortcuts import render_to_response
from django.db.models import Q, Max, Min

from libs.http import JSONResponse, JSONError
from libs import utils
from apps.account.models import  User, Member, MemberAddress, MemberCollection, MemberFootMark, UserPromoting
from apps.account.decorators import token_required
from apps.order.models import Order

@csrf_exempt
@token_required
def member_profile_save(request, user):
    try:
        if request.method == 'POST':
            name = request.POST.get("name")
            head_img = request.FILES.get("head_img")
            gender = request.POST.get("gender")
            grade = request.POST.get("grade")

            try:
                with transaction.atomic():
                    #判断name是否已经存在
                    if name:
                        name_count = Member.objects.filter(user__name=name).exclude(user__pk=user.pk).count()
                        if name_count > 0:
                            return JSONError(u'昵称已经存在!')

                        user.name = name
                        user.save()

                    if gender:
                        user.gender = gender
                        user.save()

                    member = user.bind_member
                    if grade:
                        member.grade_id = grade
                        member.save()

                    if head_img:
                        unixtime = int(time.mktime(timezone.now().timetuple()))
                        file_name = "member/%d_%d.png" % (user.pk,unixtime)

                        f = open(os.path.join(settings.MEDIA_ROOT, file_name), 'wb')
                        for chunk in head_img.chunks(chunk_size=1024):
                            f.write(chunk)
                        f.close()

                        member.icon = file_name
                        member.save()
            except KeyError, e:
                return JSONError("参数无效:" + e.message)
        else:
            return JSONError(u'必须以POST方式请求!')

    except Exception,e:
        traceback.print_exc()
        return JSONError("资料更新失败！")

    return JSONResponse({'data':{}})

@csrf_exempt
@token_required
def member_payment_save(request, user):
    params = json.loads(request.body)

    try:
        user.member_user.pay_mode = params['pay_mode']
        user.member_user.pay_account = params['pay_account']
        user.member_user.pay_name = params['pay_name']
        user.member_user.save()
        return JSONResponse({'data':{}})
    except KeyError, e:
        return JSONError("参数无效:" + e.message)
    except Exception,e:
        return JSONError(str(e))

@csrf_exempt
@token_required
def member_profile(request, user):
    data = {
        'name': user.name,
        'user': user.pk,
        'type': user.type,
        'gender': user.gender,
        'balance': user.balance,
        'promoting_amount':user.promoting_amount,
        'product_collected_count':MemberCollection.objects.filter(type=MemberCollection.PRODUCT, create_user=user).count(),
    }

    data['member'] = user.bind_member.to_api_dict()
    return JSONResponse({'data': data})

@csrf_exempt
@token_required
def member_blanace(request, user):
    if user.type == User.MEMBER:
        member = user.member_user
        balance = member.balance
        data ={'balance':balance}
        return JSONResponse({'data': data})
    else:
        return JSONError("身份有误!")

@csrf_exempt
@token_required
def collection_list(request, user):
    type = request.GET.get('type')
    rows = MemberCollection.objects.filter(create_user=user, type=type)

    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        item = row.to_dict(user)
        if item['object'] == None:
            row.delete()
            continue
        data.append(item)

    return JSONResponse({'data':data})


@csrf_exempt
@token_required
def member_footmark_list(request, user):
    type = request.GET.get('type')
    rows = MemberFootMark.objects.filter(create_user=user, type=type)

    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        item = row.to_dict(user)
        data.append(item)

    return JSONResponse({'data':data})

@csrf_exempt
@token_required
def member_promoting_list(request, user):
    rows = UserPromoting.objects.filter(src_user=user)

    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        item = row.to_api_dict()
        if row.dest_user.bind_member and row.dest_user.bind_member.level and row.dest_user.bind_member.level.name:
            item['dest_user_level_text'] = row.dest_user.bind_member.level.name
        else:
            item['dest_user_level_text'] = "未购买会员"

        data.append(item)

    return JSONResponse({'data':data})

@csrf_exempt
@token_required
def collection_add(request, user):
    type = request.GET.get('type')
    object_id = request.GET.get('object')

    MemberCollection.objects.get_or_create(
        type=type,
        object_id=object_id,
        create_user=user
    )
    return JSONResponse({'data': {}})

@csrf_exempt
@token_required
def collection_del(request, user):
    id = request.GET.get('id')
    row = MemberCollection.objects.get(id=id,create_user=user)
    row.delete()
    return JSONResponse({'data':{}})

@csrf_exempt
@token_required
def address_list(request, user):
    rows = MemberAddress.objects.filter(create_user=user)

    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        item = row.to_dict()
        data.append(item)

    return JSONResponse({'data':data})

@csrf_exempt
@token_required
def address_save(request, user):
    data = json.loads(request.body)
    id = request.GET.get('id')

    if id:
        MemberAddress.objects.filter(id=id).update(
            address = data['address'],
            name = data['name'],
            mobile = data['mobile']
        )
    else:
        MemberAddress.objects.create(
            address=data['address'],
            name=data['name'],
            mobile=data['mobile'],
            create_user=user
        )
    return JSONResponse({'data':{}})

@csrf_exempt
@token_required
def address_del(request, user):
    id = request.GET.get('id')
    row = MemberAddress.objects.get(id=id)
    row.delete()
    return JSONResponse({'data':{}})
