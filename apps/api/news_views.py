# coding=utf-8

import json
import traceback

from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.utils import timezone
from django.db import transaction
from django.http import HttpResponse
from django.db.models import Q

from libs.http import JSONResponse, JSONError
from libs import utils
from apps.account.decorators import token_required
from apps.news.models import News


def news_list(request):
    rows = News.objects.filter(type=News.TYPE_NOTICE)
    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        item = row.to_api_dict()
        del item['content']
        data.append(item)

    return JSONResponse({'data':data})


def news_detail_by_id(request,id):
    try:
        row = News.objects.get(pk=id)
        data = row.to_api_dict()
        return JSONResponse({'data':data})
    except Exception,e:
        print e

    return JSONError(u'读取信息失败!')



@csrf_exempt
def news_detail_by_title(request):
    try:
        p = json.loads(request.body)
        title = p['title']
        row = News.objects.get(type=News.TYPE_SIGNLE,title=title)
        data = row.to_api_dict()
        return JSONResponse({'data':data})
    except Exception,e:
        print e

    return JSONError(u'读取信息失败!')

