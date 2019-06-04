# coding=utf-8

import base64
import json
import os
import traceback
import datetime
import random
import re
import urllib2
import urllib

import time

from django.conf import settings
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.db.models.aggregates import Max
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import Group, Permission

import libs
from libs.http import JSONResponse, JSONError, JSONErrorCode
from libs import utils
from apps.account.tokens import token_generator
from apps.account.models import User, Member, UserPromoting
from apps.account.decorators import token_required
from libs.utils import year_delta
from apps.system.models import Visitor, Feedback, Version, VCode
from libs.sms import SMS


@csrf_exempt
def verifycode(request):
    #引入绘图模块
    from PIL import Image, ImageDraw, ImageFont
    #引入随机函数模块
    import random
    #定义变量，用于画面的背景色、宽、高
    bgcolor = (random.randrange(20, 100), random.randrange(
        20, 100), 255)
    width = 100
    height = 25
    #创建画面对象
    im = Image.new('RGB', (width, height), bgcolor)
    #创建画笔对象
    draw = ImageDraw.Draw(im)
    #调用画笔的point()函数绘制噪点
    for i in range(0, 100):
        xy = (random.randrange(0, width), random.randrange(0, height))
        fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
        draw.point(xy, fill=fill)
    #定义验证码的备选值
    str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
    #随机选取4个值作为验证码
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]
    #构造字体对象
    font = ImageFont.truetype(os.path.join(settings.BASE_DIR, "static") + '/FreeMono.ttf', 23)
    #构造字体颜色
    fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
    #绘制4个字
    draw.text((5, 2), rand_str[0], font=font, fill=fontcolor)
    draw.text((25, 2), rand_str[1], font=font, fill=fontcolor)
    draw.text((50, 2), rand_str[2], font=font, fill=fontcolor)
    draw.text((75, 2), rand_str[3], font=font, fill=fontcolor)
    #释放画笔
    del draw
    #存入session，用于做进一步验证
    request.session['verifycode'] = rand_str
    #内存文件操作
    import io
    # buf = io.StringIO()
    buf = io.BytesIO()
    #将图片保存在内存中，文件类型为png
    im.save(buf, 'png')


    #将内存中的图片数据返回给客户端，MIME类型为图片png
    return HttpResponse(buf.getvalue(), 'image/png')

@csrf_exempt
def mobile_vcode(request):
    mobile = request.GET.get('mobile')
    pvcode = request.GET.get('pvcode', '')
    if mobile == '' or  not mobile:
        return JSONError('参数无效！')

    verify_code = ""
    try:
        verify_code = request.session['verifycode']
        #del request.session['verifycode']
    except:
        pass

    if not verify_code:
        return JSONError(u'图形验证码不存在!')

    if pvcode.lower() != verify_code.lower():
        return JSONError(u'图形验证码不正确!')

    # 判断最近虽否发送过短信
    vcs = VCode.objects.filter(mobile=mobile).order_by('-id')
    if vcs.count() > 0:
        vc = vcs[0]
        if (timezone.now() - vc.add_time).seconds < 30:
            return JSONError('获取太频繁，请稍后再试！')

    vcode = random.randint(1234, 9999)
    _sms = SMS()
    #暂时注释真实发送短信接口
    resp = _sms.send_vcode(mobile, str(vcode),VCode.REGISTER)
    if not resp:
        VCode.objects.create(mobile=mobile, vcode=vcode,status = VCode.UNSUCCESS)
        return JSONError("短信发送出错。")
    # else:
    VCode.objects.create(mobile=mobile, vcode=vcode,status = VCode.OK)
    return JSONResponse({'data': {}})


@csrf_exempt
def register_check(request):
    mobile = request.GET.get('mobile')
    vcode = request.GET.get("vcode")
    referee = request.GET.get("referee")
    if mobile == '' or vcode == '':
        return JSONError('参数无效！')
    if referee != '':
        try:
            referee_user = User.objects.get(username=referee)
        except User.DoesNotExist:
            return JSONError("推荐人不存在,请检查")

    vcs = VCode.objects.filter(mobile=mobile).order_by('-id')
    if vcs.count() > 0:
        vc = vcs[0]
    else:
        return JSONError('请获取验证码！')

    if (timezone.now() - vc.add_time).seconds > 1800:
        return JSONError('验证码已过期，请重新获取！')

    if vcode != vc.vcode:
        return JSONError("验证码错误！")

    rows = Member.objects.filter(user__username=mobile)
    if rows:
        return JSONError("此手机号码已经注册！")

    return JSONResponse({'data': {}})


@csrf_exempt
def register(request):
    try:
        if request.method == 'POST':
            params = json.loads(request.body)
            vcode = params['vcode']
            username = params['username']
            password = params['password']
            weixin_id = params['weixin_id']
            referee = params['referee']

            if weixin_id == "":
                weixin_id = None

            vcs = VCode.objects.filter(mobile=username).order_by('-id')
            if vcs.count() > 0:
                vc = vcs[0]
            else:
                return JSONError('请获取验证码！')

            if (timezone.now() - vc.add_time).seconds > 1800:
                return JSONError('验证码已过期，请重新获取！')

            if vcode != vc.vcode:
                return JSONError("验证码错误！")

            if weixin_id:
                try:
                    weixin_member = Member.objects.get(weixin_id=weixin_id)
                    if weixin_member:
                        return JSONError("该微信已经绑定了其他手机，请直接登录或找回密码！")
                except KeyError, e:
                    return JSONError("参数无效:" + e.message)
                except Member.DoesNotExist:
                    pass

            try:
                user = User.objects.get(username=username)
                if user:
                    return JSONError("用户名已存在！")
            except KeyError, e:
                return JSONError("参数无效:" + e.message)
            except User.DoesNotExist:
                pass

            try:
                with transaction.atomic():
                    user = User.objects.create_user(username=username, password=password, type=User.MEMBER)
                    user.save()

                    global member
                    if referee != '':
                        referee_user = User.objects.get(username=referee)
                        if referee_user:
                            member = Member.objects.create(user=user, referee=referee_user)
                            UserPromoting.objects.create(
                                src_user=referee_user,
                                dest_user=user,
                                order_no='-',
                                create_time=timezone.now(),
                            )
                        else:
                            member = Member.objects.create(user=user)
                    else:
                        member = Member.objects.create(user=user)

                    member.weixin_id = weixin_id
                    member.save()
            except KeyError, e:
                return JSONError("参数无效:" + e.message)
            except User.DoesNotExist:
                return JSONError("推荐账号不存在！")
        else:
            return JSONError(u'必须以POST方式请求!')

    except Exception, e:
        traceback.print_exc()
        return JSONError("注册失败！")

    user.last_login = timezone.now()
    user.save()
    token = token_generator.make_token(user)

    data = {
        'token': token,
        'name': user.name,
        'user': user.pk,
        'type': user.type,
    }

    data['member'] = member.to_api_dict()

    return JSONResponse({'data': data})


@csrf_exempt
@token_required
def register_finish(request,user):
    try:
        if request.method == 'POST':
            name = request.POST.get("name")
            sex = request.POST.get("sex")
            # grade = request.POST.get("grade")
            head_img = request.FILES.get("head_img")
            # referee = request.POST.get("referee")
            # if not referee:
            #     referee = 0
            # referee = int(referee)

            if not sex:
                sex = '1'
            sex = int(sex)


            #根据birthday生成age
            # age = 0
            # try:
            #     dt_age = datetime.datetime.strptime(birthday,'%Y-%m-%d').date()
            #     now = timezone.now().date()
            #     age = year_delta(dt_age,now)
            # except Exception,e:
            #     print e
            #     return JSONError(u'生日格式不正确!')

            if not name:
                return JSONError(u'昵称为必输项!')

            if not head_img:
                return JSONError(u'头像必须上传!')

            try:
                #判断name是否已经存在
                name_count = Member.objects.filter(user__name=name).exclude(user__pk=user.pk).count()
                if name_count > 0:
                    return JSONError(u'昵称已经存在!')

                with transaction.atomic():
                    user.name = name
                    user.gender = sex
                    user.save()

                    member = user.bind_member

                    unixtime = int(time.mktime(timezone.now().timetuple()))
                    file_name = "member/%d_%d.png" % (user.pk, unixtime)

                    f = open(os.path.join(settings.MEDIA_ROOT, file_name), 'wb')
                    for chunk in head_img.chunks(chunk_size=1024):
                        f.write(chunk)
                    f.close()

                    member.icon = file_name
                    member.save()

                    return JSONResponse({'data':{}})
            except KeyError, e:
                return JSONError("参数无效:" + e.message)
            except User.DoesNotExist:
                return JSONError("资料完成失败！")
        else:
            return JSONError(u'必须以POST方式请求!')

    except Exception, e:
        traceback.print_exc()
        return JSONError("资料完成失败！")

@csrf_exempt
def auth(request):
    params = json.loads(request.body)
    if not params.has_key('username') or not params.has_key('password'):
        return JSONError('参数无效！')

    user = None
    member = None
    try:
        member = Member.objects.get(user__username=params['username'])
        user = member.user
    except Member.DoesNotExist:
        return JSONErrorCode(3, u'用户不存在!')
    except:
        pass

    if user == None:
        return JSONError('用户名或密码错误！')

    if not user.check_password(params['password']):
        return JSONError('用户名或密码错误！')

    if not user.is_active:
        return JSONError("帐号被禁用！")

    if user.type != User.MEMBER:
        return JSONError("非会员帐号不允许登录！")

    user.last_login = timezone.now()
    user.last_login_ip = request.META.get('REMOTE_ADDR')
    user.save()
    token = token_generator.make_token(user)

    data = {
        'token': token,
        # 'rc_token':member.rc_token,
        'name': user.name,
        'user': user.pk,
        # 'type': user.type,
    }

    data['member'] = member.to_api_dict()

    return JSONResponse({'data': data})


@csrf_exempt
def auth_weixin(request):
    params = json.loads(request.body)
    if not params.has_key('weixin_id'):
        return JSONError('参数无效！')

    user = None
    member = None
    try:
        member = Member.objects.get(weixin_id=params['weixin_id'])
        user = member.user
    except Member.DoesNotExist:
        return JSONErrorCode(3, u'用户不存在!')
    except Exception, e:
        print e
        return JSONError(u'登录出现错误!!')

    if not user.is_active:
        return JSONError("帐号被禁用！")

    user.last_login = timezone.now()
    user.last_login_ip = request.META.get('REMOTE_ADDR')
    user.save()
    token = token_generator.make_token(user)

    data = {
        'token': token,
        'name': user.name,
        'user': user.pk,
        'type': user.type,
    }

    data['member'] = member.to_api_dict()

    return JSONResponse({'data': data})


@csrf_exempt
def token(request, token, user):
    try:
        user = User.objects.get(pk=user)
    except User.DoesNotExist:
        return JSONError("用户不存在。")

    if token_generator.check_token(user, token):
        user.last_login = timezone.now()
        user.save()
        return JSONResponse({'data': {}})
    else:
        return JSONError("账户登录已过期，请重新登录！")


@csrf_exempt
@token_required
def user_change_password(request, user):
    params = json.loads(request.body)

    if params['password'] == '' or params['new_password'] == '':
        return JSONError('参数无效！')

    password = params['password']
    new_password = params['new_password']

    if user.check_password(password):
        user.set_password(new_password)
        user.save()
    else:
        return JSONError('原密码不正确！')

    user.token = token_generator.make_token(user)
    user.save()

    return JSONResponse({'data': {'token': user.token}})


@csrf_exempt
def reset_password_check(request):
    mobile = request.GET.get('mobile')
    vcode = request.GET.get("vcode")
    if mobile == '' or vcode == '':
        return JSONError('参数无效！')

    vcs = VCode.objects.filter(mobile=mobile).order_by('-id')
    if vcs.count() > 0:
        vc = vcs[0]
    else:
        return JSONError('请获取验证码！')

    if (timezone.now() - vc.add_time).seconds > 1800:
        return JSONError('验证码已过期，请重新获取！')

    if vcode != vc.vcode:
        return JSONError("验证码错误！")

    rows = Member.objects.filter(user__username=mobile)
    if not rows:
        return JSONError("此手机号码未注册！")

    return JSONResponse({'data': {}})


@csrf_exempt
def reset_password(request):
    """重置密码"""
    try:
        params = json.loads(request.body)
        username = params['username']
        new_password = params['new_password']
        vcode = params['vcode']
    except Exception, e:
        traceback.print_exc()
        return JSONError('参数有误！')

    try:
        vc = VCode.objects.filter(mobile=username)[0]
    except VCode.DoesNotExist:
        return JSONError('请获取验证码！')

    if (timezone.now() - vc.add_time).seconds > 1800:
        return JSONError('验证码已过期，请重新获取！')

    if vcode != vc.vcode:
        return JSONError("验证码错误！")

    user = None
    try:
        member = Member.objects.get(user__username=username)
        user = member.user
    except:
        pass

    if user == None:
        return JSONError("用户不存在！")

    user.set_password(new_password)
    user.save()
    return JSONResponse({'data': {}})


@csrf_exempt
@token_required
def visit(request, user):
    """访问记录"""
    try:
        data = json.loads(request.body)
        Visitor.objects.create(
            start_time=data['start_time'],
            end_time=data['end_time'],
            platform=data['platform'],
            IP=data['ip'],
            device_machine=data['device_machine'],
            resolution=data['resolution'],
            os_version=data['os_version'],
            app_version=data['app_version'],
            network_type=data['network_type'],
            device_UID=data['device_UID'],
            user=user
        )
    except Exception, e:
        traceback.print_exc()
        return JSONError(str(e))

    return JSONResponse({'data': {}})


@csrf_exempt
@token_required
def feedback_submit(request, user):
    params = json.loads(request.body)
    if params['type'] == '' or params['content'] == '':
        return JSONError('参数无效！')

    try:
        Feedback.objects.create(type=params['type'], content=params['content'], create_user_id=request.GET.get('user'))
    except Exception, e:
        return JSONError('提交出错！')

    return JSONResponse({'data': {}})


@csrf_exempt
@token_required
def feedback_mine(request, user):
    rows = Feedback.objects.filter(create_user_id=request.GET.get('user'))
    data = []
    for row in rows:
        data.append(row.to_dict())
    rows.filter(reply_content__isnull=False).update(reply_read=1)
    return JSONResponse({'data': data})


@csrf_exempt
@token_required
def feedback_mine_unread_count(request, user):
    count = Feedback.objects.filter(create_user_id=request.GET.get('user'), reply_content__isnull=False,
                                    reply_read=False).count()
    return JSONResponse({'data': {'count': count}})


@csrf_exempt
def version_app(request):
    platform = request.GET.get('platform',Version.ANDROID)
    # platform = 1  # 只显示android
    rows = Version.objects.filter(platform=platform)
    data = {}
    if rows.count() > 0:
        row = rows[0]
        data['data'] = {'version': row.version, 'title': row.title, 'content': row.content}
    else:
        data['data'] = {'version': '0', 'title': '', 'content': ''}
    return JSONResponse(data)

@csrf_exempt
def version_ios(request):
    data = {}
    data['data'] = settings.APPLE_STATE
    return JSONResponse(data)
