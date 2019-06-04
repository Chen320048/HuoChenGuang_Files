#coding=utf-8

from django.conf import settings
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.utils import timezone

import time
import uuid
import hashlib
import urllib2
import json

from libs.utils import strftime

class MyAuthenticationForm(AuthenticationForm):
    class Meta:
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(AuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].error_messages = {'required': '请输入账号！'}
        self.fields['password'].error_messages = {'required': '请输入密码！'}

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,password=password)
            if self.user_cache is None:
                raise forms.ValidationError("用户名或密码错误！")
            elif not self.user_cache.is_active:
                raise forms.ValidationError("账号被禁用！")
        return self.cleaned_data
