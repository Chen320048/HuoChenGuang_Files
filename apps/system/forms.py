# coding=utf-8

from django import forms
from django.contrib.auth import authenticate
from django.utils import timezone

from models import Feedback, Version, VCode
from apps.account.models import User


class MyModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label=u"原密码", max_length=30, widget=forms.PasswordInput(
        attrs={'size': 20, 'class': 'easyui-textbox', 'required': 'true'}), required=True)
    new_password = forms.CharField(label=u"新密码", max_length=30, widget=forms.PasswordInput(
        attrs={'size': 20, 'class': 'easyui-textbox', 'required': 'true'}), required=True)
    new_password_repeat = forms.CharField(label=u"新密码确认", max_length=30, widget=forms.PasswordInput(
        attrs={'size': 20, 'class': 'easyui-textbox', 'required': 'true'}), required=True)

    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.username = None

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']
        user = authenticate(username=self.username, password=old_password)
        if user == None:
            raise forms.ValidationError(u"原密码错误，请重新输入！")
        return old_password

    def clean_new_password_repeat(self):
        new_password = self.cleaned_data['new_password']
        new_password_repeat = self.cleaned_data['new_password_repeat']
        if new_password != new_password_repeat:
            raise forms.ValidationError(u"两次输入的密码不一致，请重新输入！")
        return new_password_repeat


class ResetPasswordForm(forms.Form):
    username = forms.CharField(label=u"账号", max_length=30, widget=forms.TextInput(
        attrs={'size': 20, 'class': 'easyui-textbox', 'required': 'true'}), required=True)
    new_password = forms.CharField(label=u"新密码", max_length=30, widget=forms.PasswordInput(
        attrs={'size': 20, 'class': 'easyui-textbox', 'required': 'true'}), required=True)
    new_password_repeat = forms.CharField(label=u"新密码确认", max_length=30, widget=forms.PasswordInput(
        attrs={'size': 20, 'class': 'easyui-textbox', 'required': 'true'}), required=True)
    vcode = forms.CharField(label=u"验证码", max_length=6,
                            widget=forms.TextInput(attrs={'size': 10, 'class': 'easyui-textbox', 'required': 'true'}),
                            required=True)

    def clean_vcode(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(u"用户帐号不存在！")

        rs = VCode.objects.filter(mobile=username).order_by("-id")
        if rs.count() == 0:
            raise forms.ValidationError(u'请发送验证码！')
        vc = rs[0]
        if (timezone.now() - vc.add_time).seconds > 1800:
            raise forms.ValidationError(u'验证码已过期，请重新发送！')
        if vc.vcode != self.cleaned_data['vcode']:
            raise forms.ValidationError(u'验证码错误！')
        return self.cleaned_data['vcode']

    def clean_new_password_repeat(self):
        new_password = self.cleaned_data['new_password']
        new_password_repeat = self.cleaned_data['new_password_repeat']
        if new_password != new_password_repeat:
            raise forms.ValidationError(u"两次输入的密码不一致，请重新输入！")
        return new_password_repeat


class FeedbackForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = Feedback
        widgets = {
            'title': forms.TextInput(attrs={'size': 40, 'class': 'easyui-textbox', 'data-options': "'required':true"}),
            'content': forms.TextInput(attrs={'style': 'width:90%;height:80px', 'class': 'easyui-textbox',
                                              'data-options': "'required':true,'multiline':true"}),
            'create_user': forms.HiddenInput(),
        }


class VersionForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        model = Version

        widgets = {
            'platform': forms.Select(attrs={'class': 'easyui-combobox', 'data-options': "'required':true", "style":'width:100px'}),
            'version': forms.TextInput(attrs={'class': 'easyui-textbox', 'data-options': "'required':true"}),
            # 'filename': forms.TextInput(attrs={'class':'easyui-filebox', 'data-options':"'required':true,buttonText:'选择'", 'style':'width:300px'}),
            'title': forms.TextInput(attrs={'size': 80, 'class': 'easyui-textbox', 'data-options': "'required':true"}),
            'content': forms.TextInput(attrs={'style': 'width:90%;height:80px', 'class': 'easyui-textbox',
                                              'data-options': "'required':true,'multiline':true"}),
            'created': forms.HiddenInput(),
            'user': forms.HiddenInput()
        }

        exclude = {}


