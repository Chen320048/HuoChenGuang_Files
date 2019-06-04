# coding=utf-8

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group, Permission
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate

from models import User, KindergartenManager
from apps.classes.models import Kindergarten,Classes


class MyModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class ProvinceChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class SingleMultipleChoiceField(forms.MultipleChoiceField):
    widget = forms.Select

    def to_python(self, value):
        if not value:
            return []
        return [value]

    def validate(self, value):
        if self.required and not value:
            raise ValidationError(self.error_messages['required'])
            # if not self.valid_value(value):
            #    raise ValidationError(self.error_messages['invalid_choice'] % {'value': value})

class AccountForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super(AccountForm, self).__init__(*args, **kwargs)
    #
    #     self.fields['groups'] = SingleMultipleChoiceField(widget=forms.Select(attrs={'style':'width:250px;', 'class':'easyui-combobox', 'required':'true', 'editable':'false', 'data-options':"url:'/account/group/data/',method:'get',valueField:'id',textField:'name'"}))
    #     self.fields['groups'].help_text = ''
    #     self.fields['groups'].label = u'角色'
    #     self.fields['groups'].required = True

    class Meta:
        model = User
        fields = ('username', 'password', 'name','type','is_active',)
        widgets = {
            'username': forms.TextInput(attrs={'size': 30, 'class':'easyui-textbox easyui-validatebox', 'required':'true'}),
            'name': forms.TextInput(attrs={'size': 50, 'class':'easyui-textbox', 'required':'true'}),
            'password': forms.TextInput(attrs={'class':'easyui-textbox easyui-validatebox', 'required':'true'}),
            # 'gender': forms.Select(attrs={'class': 'easyui-combobox easyui-validatebox', 'required': 'true', 'style':'width:100px'}),
            'type': forms.HiddenInput(),
            # 'is_superuser': forms.CheckboxInput(attrs={'class': 'easyui-switchbutton', 'onText': "启用", 'offText': "禁用", 'value': 'true'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'easyui-switchbutton', 'onText': "启用", 'offText': "禁用", 'value': 'true'}),
        }


class KindergartenManagerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(KindergartenManagerForm, self).__init__(*args, **kwargs)
        # self.fields['groups'] = SingleMultipleChoiceField(widget=forms.Select(attrs={'style':'width:250px;', 'class':'easyui-combobox', 'required':'true', 'editable':'false', 'data-options':"url:'/account/group/data/',method:'get',valueField:'id',textField:'name'"}))
        # self.fields['groups'].help_text = ''
        # self.fields['groups'].label = u'角色'
        # self.fields['groups'].required = True
        self.fields['kindergarten'] = MyModelChoiceField(
            label=u'幼儿园',
            queryset=Kindergarten.objects.all(),
            required=False,
            empty_label=''
        )
        self.fields['kindergarten'].widget.attrs['class'] = 'easyui-validatebox'
    class Meta:
        model = User
        fields = ('username', 'password', 'name','is_active', 'type')
        widgets = {
            'username': forms.TextInput(attrs={'size': 30, 'class': 'easyui-textbox easyui-validatebox', 'required': 'true'}),
            'name': forms.TextInput(attrs={'size': 50, 'class': 'easyui-textbox', 'required': 'true'}),
            'password': forms.TextInput(attrs={'class': 'easyui-textbox easyui-validatebox', 'required': 'true'}),
            'type': forms.HiddenInput(),
            # 'gender': forms.Select(attrs={'class': 'easyui-combobox easyui-validatebox', 'required': 'true', 'style': 'width:100px'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'easyui-switchbutton', 'onText': "启用", 'offText': "禁用", 'value': 'true'}),
        }


class ChangeKindergartenManagerForm(AccountForm):
    def __init__(self, *args, **kwargs):
        super(ChangeKindergartenManagerForm, self).__init__(*args, **kwargs)
        del self.fields['password']


class TeacherForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TeacherForm, self).__init__(*args, **kwargs)
        self.fields['classes'] = SingleMultipleChoiceField(widget=forms.Select(attrs={'style':'width:100px;', 'class':'easyui-combobox', 'required':'true', 'editable':'false', 'data-options':"url:'/account/class/data/',method:'get',valueField:'id',textField:'name'"}))
        self.fields['classes'].help_text = ''
        self.fields['classes'].label = u'班级'

    class Meta:
        model = User
        fields = ('username','name','password','is_active',)
        widgets = {
            'username': forms.TextInput(
                attrs={'size': 30, 'class': 'easyui-textbox easyui-validatebox', 'required': 'true'}),
            'name': forms.TextInput(attrs={'size': 50, 'class': 'easyui-textbox', 'required': 'true'}),
            'password': forms.TextInput(attrs={'class': 'easyui-textbox easyui-validatebox', 'required': 'true'}),
            # 'gender': forms.Select(
            #     attrs={'class': 'easyui-combobox easyui-validatebox', 'required': 'true', 'style': 'width:100px'}),
            'is_active': forms.CheckboxInput(
                attrs={'class': 'easyui-switchbutton', 'onText': "启用", 'offText': "禁用", 'value': 'true'}),
        }

class ChangeTeacherForm(TeacherForm):
    def __init__(self, *args, **kwargs):
        super(ChangeTeacherForm, self).__init__(*args, **kwargs)
        del self.fields['password']


class AccountEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('name', 'is_active', )
        widgets = {
            'name': forms.TextInput(attrs={'size': 50, 'class':'easyui-textbox', 'required':'true'}),
            'type': forms.HiddenInput(),
        }


class ChangeAccountForm(AccountForm):
    def __init__(self, *args, **kwargs):
        super(ChangeAccountForm, self).__init__(*args, **kwargs)
        # del self.fields['username']
        del self.fields['password']


class GroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)

        self.fields['permissions'].help_text = ''

    class Meta:
        model = Group
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'easyui-textbox', 'required': 'true'}),
            'permissions': forms.SelectMultiple(
                attrs={'style': 'width:300px;', 'class': 'easyui-combobox', 'required': 'true', 'editable': 'false',
                       'valueField': 'id', 'textField': 'text', 'groupField': 'group',
                       'data-options': "url:'/account/permission/data/',method:'get',multiple:false"}),
        }


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

class NormalAccountForm(AccountForm):
    def __init__(self, *args, **kwargs):
        super(NormalAccountForm, self).__init__(*args, **kwargs)
        del self.fields['groups']
