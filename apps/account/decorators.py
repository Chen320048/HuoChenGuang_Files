#coding=utf-8

from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.utils.functional import wraps

from libs.http import JSONResponse, JSONTokenExpired

def token_required(view_func):
    """Decorator which ensures the user has provided a correct user and token pair."""

    @csrf_exempt
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.GET.get('user')
        token = request.GET.get('token')
        if user and token:
            user = authenticate(pk=user, token=token)
            if user:
                return view_func(request, user, *args, **kwargs)
        #return HttpResponseForbidden()
        return JSONTokenExpired()
    return _wrapped_view

