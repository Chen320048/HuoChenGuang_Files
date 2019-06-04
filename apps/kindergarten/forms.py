# coding:utf-8
from django import forms

from models import *


class SubjectForm(forms.ModelForm):
    class Meta:
        model=Subject
        fields = '__all__'

class IcomForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(IcomForm, self).__init__(*args, **kwargs)
        self.fields['code'] = forms.ModelChoiceField(
            label=u'科目',
            queryset=Subject.objects.filter(type=Subject.ICOME),
            required=False,
            empty_label=''
        )
        self.fields['code'].widget.attrs['class'] = 'easyui-validatebox'
    class Meta:
        model=Icome
        exclude=('submitter','kindergarten')


class ExpenseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        self.fields['code'] = forms.ModelChoiceField(
            label=u'科目',
            queryset=Subject.objects.filter(type=Subject.EXPENSE),
            required=False,
            empty_label=''
        )
        self.fields['code'].widget.attrs['class'] = 'easyui-validatebox'
    class Meta:
        model=Expense
        exclude=('submitter','kindergarten')
        widgets = {
            'notes':forms.Textarea(attrs={'style': 'width:300px;height:100px;', 'class': 'easyui-textbox',
                                                 'data-options': "multiline:true"}),
        }