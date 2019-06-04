# -*- coding: utf-8 -*-

from django import forms
from django.utils import timezone

from models import *

class DrawingAccountForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = DrawingAccount
        widgets = {
            'account_number': forms.TextInput(attrs={'size': 30, 'class': 'easyui-textbox', 'data-options': "'required':true"}),
            'account_name': forms.TextInput(
                attrs={'size': 30, 'class': 'easyui-textbox', 'data-options': "'required':true"}),
            'account_bank': forms.TextInput(
                attrs={'size': 30, 'class': 'easyui-textbox'}),
        }


    def save(self, commit=True, request=None, *args, **kwargs):
        instance = super(DrawingAccountForm, self).save(commit=False)
        if instance.id == None:
            instance.create_user = request.user
        instance.save()
        return instance


class DrawingForm(forms.Form):
    total_fee = forms.CharField(label=u"提现金额", max_length=30, widget=forms.TextInput(
        attrs={'size': 20, 'class': 'easyui-textbox', 'required': 'true'}), required=True)

    choices = list(DrawingAccount.TYPE_CHOICES)
    choices.insert(0, ('', ''))
    type = forms.CharField(
        label=u"提现方式",
        max_length=30,
        widget=forms.Select(
            attrs={'style': 'width:130px', 'class': 'easyui-combobox', 'required': 'true', 'data-options':'onChange:onTypeChange'},
            choices=choices,
        ),
        required=True)
    account_number = forms.CharField(label=u"账户", max_length=30, widget=forms.TextInput(
        attrs={'size': 20, 'class': 'easyui-textbox', 'required': 'true'}), required=True)
    account_name = forms.CharField(label=u"户名", max_length=30, widget=forms.TextInput(
        attrs={'size': 20, 'class': 'easyui-textbox', 'required': 'true'}), required=True)
    account_bank = forms.CharField(label=u"银行", max_length=30, widget=forms.TextInput(
        attrs={'size': 20, 'class': 'easyui-textbox'}), required=False)

class CommissionRatioForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = "__all__"
        model = CommissionRatio
        widgets = {
            'user': forms.TextInput(attrs={'size': 30, 'class':'easyui-numberbox', 'required':'true'}),
            'platform': forms.TextInput(attrs={'size': 30, 'class': 'easyui-numberbox', 'required': 'true'}),
        }

    def clean(self):
        data = self.cleaned_data
        if data['user'] + data['platform'] <> 100:
            raise forms.ValidationError(u'无效的比例！')
        return data