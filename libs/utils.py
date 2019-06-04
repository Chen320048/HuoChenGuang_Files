#coding=utf-8

from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.db import models
from django.http import HttpResponse
from django.conf import settings
from django.utils.decorators import available_attrs

from functools import wraps
from decimal import *
from hashlib import md5 as md5_constructor
from PIL import Image
from django.utils import timezone
# from apps.system.models import Token

import random
import datetime
import calendar
import hashlib
import os
import sys
import types
import json
import math
import requests

def calc_sha1(file):
    sha1obj = hashlib.sha1()
    sha1obj.update(file)
    hash = sha1obj.hexdigest()
    print(hash)
    return hash
 
def calc_md5(file):
    md5obj = hashlib.md5()
    md5obj.update(file)
    hash = md5obj.hexdigest()
    print(hash)
    return hash

def console(out):
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
    print out
    print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'

def get_page_info(request):
    try:
        page_index = int(request.POST.get('page')) - 1
    except:
        page_index = 0
    if page_index < 0: page_index = 0
        
    try:
        page_size = int(request.POST.get("page_size"))
    except:
        page_size = settings.PAGE_SIZE
    
    return page_index,page_size

def get_page_data(request, rows):
    """读取分页数据"""
    try:
        page = request.POST.get('page')
        if page == None:
            page = request.GET.get('page')
        page_index = int(page) - 1
    except:
        page_index = 0
    page_size = request.POST.get("page_size") or request.GET.get("page_size")
    page_size2 =  request.POST.get("rows")
    if page_size != None :
        page_size = int(page_size)
        rows, total = get_page_data_by_index_size(rows, page_index, page_size)
    elif  page_size2 != None :
        page_size2 = int(page_size2)
        rows, total = get_page_data_by_index_size(rows, page_index, page_size2)
    else:
        rows, total = get_page_data_by_index(rows, page_index)
    return rows, total

def get_get_page_data(request, rows):
    """读取分页数据"""
    try:
        page_index = int(request.GET.get('page')) - 1
    except:
        page_index = 0
    page_size = request.GET.get("page_size")
    page_size2 =  request.GET.get("rows")
    if page_size != None :
        page_size = int(page_size)
        rows, total = get_page_data_by_index_size(rows, page_index, page_size)
    elif  page_size2 != None :
        page_size2 = int(page_size2)
        rows, total = get_page_data_by_index_size(rows, page_index, page_size2)
    else:
        rows, total = get_page_data_by_index(rows, page_index)
    return rows, total


def get_page_data_by_index(rows, page_index):
    """读取分页数据"""
    page_size = settings.PAGE_SIZE    
    rows, total = get_page_data_by_index_size(rows, page_index, page_size)
    return rows, total

def get_page_data_by_index_size(rows, page_index, page_size):
    """读取分页数据"""
    ##读取每页显示的记录条数 
    if page_index < 0 : page_index = 0
    begin = page_index * page_size
    end = (page_index + 1) * page_size
    return rows[begin:end], len(rows)

def strfdate(d):
    if d:
        return d.strftime('%Y-%m-%d')
    else:
        return ''

def strftime(t):
    if t:
        return t.strftime('%Y-%m-%d %H:%M')
    else:
        return ''

def strftime_m(t):
    if t:
        return t.strftime('%H:%M')
    else:
        return ''

def strftime_s(t):
    if t:
        return t.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return ''

def strfshorttime(t):
    if t:
        return t.strftime('%m-%d %H:%M')
    else:
        return ''

def dump_form_errors(form):
    result = []
    for i in range(0, len(form.errors.keys())):
        name = form.errors.keys()[i]
        if name == '__all__':
            err = form.errors.values()[i][0]
        else:
            err = form.fields.get(name).label + ' - ' + ','.join(form.errors.values()[i])
        result.append(err)
    print result
    return '<br>'.join(result)

def read_file(fn, buf_size=262144):
    f = open(fn, "rb")
    while True:
        c = f.read(buf_size)
        if c:
            yield c
        else:
            break
    f.close()

if hasattr(random, 'SystemRandom'):
    randrange = random.SystemRandom().randrange
else:
    randrange = random.randrange
_MAX_CSRF_KEY = 18446744073709551616L     # 2 << 63
 
def _get_new_submit_key():
    return md5_constructor("%s%s" % (randrange(0, _MAX_CSRF_KEY), settings.SECRET_KEY)).hexdigest()
 
def anti_resubmit(page_key=''):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if request.method == 'GET':
                request.session['%s_submit' % page_key] = _get_new_submit_key()
                print 'session:' + request.session.get('%s_submit' % page_key)
            elif request.method == 'POST':
                old_key = request.session.get('%s_submit' % page_key, '')
                if old_key == '':
                    from django.http import HttpResponseRedirect
                    return HttpResponseRedirect('/page_expired/')
                request.session['%s_submit' % page_key] = ''
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def number2CNY(nin=None):
    def IIf( b, s1, s2):
        if b:
            return s1
        else:
            return s2

    cs =(u'零',u'壹',u'贰',u'叁',u'肆',u'伍',u'陆',u'柒',u'捌',u'玖',u'◇',u'分',u'角',u'圆',u'拾',u'佰',u'仟',u'万',u'拾',u'佰',u'仟',u'亿',u'拾',u'佰',u'仟',u'万')
    st = ''
    st1=''
    s = '%0.2f' % (nin)
    sln =len(s)
    if sln > 15: 
        return None

    fg = (nin<1)
    for i in range(0, sln-3):
        ns = ord(s[sln-i-4]) - ord('0')
        st=IIf((ns==0)and(fg or (i==8)or(i==4)or(i==0)), '', cs[ns]) + IIf((ns==0)and((i<>8)and(i<>4)and(i<>0)or fg and(i==0)),'', cs[i+13]) + st
        fg = (ns==0)

    fg = False
    for i in [1,2]:
        ns = ord(s[sln-i]) - ord('0')
        st1 = IIf((ns==0)and((i==1)or(i==2)and(fg or (nin<1))), '', cs[ns]) + IIf((ns>0), cs[i+10], IIf((i==2) or fg, '', u'整')) + st1
        fg = (ns==0)
    st.replace(u'亿万',u'万')
    return IIf( nin==0, u'零', st + st1)



def add_month_interval(dt,inter):
    def _add_month_interval (dt,inter):
        m=dt.month+inter-1
        y=int(dt.year+math.floor(m/12))
        m=m % 12 +1
        return (y,m)
    
    y,m=_add_month_interval(dt,inter)
    y2,m2=_add_month_interval(dt,inter+1)
    maxD=( datetime.date(y2,m2,1)-datetime.timedelta(days=1) ).day
    d= dt.day<=maxD and dt.day or maxD
    return datetime.date(y,m,d)

def resize_image(filename, w):
    img = Image.open(filename)
    wpercent = (w/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    img = img.resize((w,hsize), Image.ANTIALIAS)
    img.save(filename)

def format_money(n, sep = ','):
    s = str(abs(n))[::-1]
    groups = []
    i = 0
    while i < len(s):
        groups.append(s[i:i+3])
        i+=3
    retval = sep.join(groups)[::-1]
    if n < 0:
        return '-%s' % retval
    else:
        return retval

def form_data_file_save(file,file_name):
    f = None
    try:
        f = open(os.path.join(settings.MEDIA_ROOT, file_name), 'wb')
        for chunk in file.chunks(chunk_size=1024):
            f.write(chunk)
        return True
    except Exception,e:
        print e

    finally:
        if f:
            f.close()

    return False

def month_delta(x,y):
    """暂不考虑day, 只根据month和year计算相差月份
    Parameters
    ----------
    x, y: 两个datetime.datetime类型的变量

    Return
    ------
    differ: x, y相差的月份
    """
    month_differ = abs((x.year - y.year) * 12 + (x.month - y.month) * 1)
    return month_differ


def year_delta(x,y):
    months = month_delta(x,y)
    return months / 12

def handle_image_upload(request,path_and_rename,file,name,instace):
    def _save_image(file, instance):
        if request.FILES.has_key(name):
            file = request.FILES[name]
            filename = "%s/%d-%s.%s" % (
                path_and_rename.path, instance.id, timezone.now().strftime('%Y%m%d%H%M%S%f'),file.name.split('.')[-1])
            full_filename = "%s/%s" % (settings.MEDIA_ROOT, filename)
            with open(full_filename, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            resize_image(full_filename, 800)
            return filename
    return _save_image(file,instance=instace)


def getMonthFirstDayAndLastDay(year=None, month=None):
    """
    :param year: 年份，默认是本年，可传int或str类型
    :param month: 月份，默认是本月，可传int或str类型
    :return: firstDay: 当月的第一天，datetime.date类型
              lastDay: 当月的最后一天，datetime.date类型
    """
    if year:
        year = int(year)
    else:
        year = datetime.date.today().year

    if month:
        month = int(month)
    else:
        month = datetime.date.today().month

    # 获取当月第一天的星期和当月的总天数
    firstDayWeekDay, monthRange = calendar.monthrange(year, month)

    # 获取当月的第一天
    firstDay = datetime.date(year=year, month=month, day=1)
    lastDay = datetime.date(year=year, month=month, day=monthRange)

    first_datetime = datetime.datetime(year,month,1,0,0,0)
    last_datetime = datetime.datetime(year, month, monthRange,11,59,59)
    return firstDay, lastDay,first_datetime,last_datetime





