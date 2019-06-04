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
from apps.advert.models import Advert

def advert_list(request):
    loction = int(request.GET.get("loc", Advert.APP_HOME))
    rows = Advert.objects.filter(location=loction).exclude(remove_time__isnull=False).order_by('-position','-id')

    rows, total = utils.get_page_data(request, rows)

    data = []
    for row in rows:
        item = row.to_api_dict()
        data.append(item)

    return JSONResponse({'data':data})


def advert_video(request):
    adv = Advert.objects.filter(location=Advert.VIDEO).exclude(remove_time__isnull=False).order_by('-id').first()

    if adv:
        return JSONResponse({'data':adv.to_api_dict()})
    else:
        return JSONResponse({})

