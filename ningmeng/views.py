# coding=utf-8

from django.conf import settings



def global_context(request):
    return {
        'settings': settings,
    }
