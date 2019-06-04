# coding:utf-8
from django import forms

from models import *
from apps.account.models import User

class MyModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name

class SingleMultipleChoiceField(forms.MultipleChoiceField):
    widget = forms.Select


class AttendanceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)
        self.fields['student'] = SingleMultipleChoiceField(widget=forms.TextInput(attrs={'style':'width:100px;', 'class':'easyui-combobox', 'required':'true','data-options':"url:'/attendance/student/data/',method:'get',valueField:'id',textField:'name'"}))
        self.fields['student'].help_text = ''
        self.fields['student'].label = u'学生'
        self.fields['student'].readonly = True
    class Meta:
        model = Attendance
        fields = ('status','notes',)
        widgets = {
            'notes': forms.Textarea(attrs={'style': 'width:300px;height:60px;', 'class': 'easyui-textbox',
                                           'data-options': "multiline:true"}),
        }
class AttendanceEditForm(AttendanceForm):
    def __init__(self, *args, **kwargs):
        super(AttendanceEditForm, self).__init__(*args, **kwargs)
        del self.fields['student']


class RefundSubForm(forms.ModelForm):
    # field_order = []  # 根据Meta的fields的字段进行排序规则,fields没有的字段会放到列表最后
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')  # 弹出request对象
        super(RefundSubForm, self).__init__(*args, **kwargs)
        user = self.request.user  # 使用request进行操作
        students = Student.objects.all()
        if user.type == User.TEACHER:
            students = students.filter(classes__class_teacher=user.bind_teacher)
        elif user.type == User.KINDERGARTENOR:
            students = students.filter(classes__grade__kindergarten=user.bind_kindergartenor.kindergarten)
        self.fields['student'] = MyModelChoiceField(
            label=u'学生',
            queryset=students,
            required=True,
            empty_label=''
        )
    class Meta:
        model = Absence
        fields = ('days','balance','submit_notes',)
        widgets = {
            'submit_notes': forms.Textarea(attrs={'style': 'width:300px;height:100px;', 'required':True,'class': 'easyui-textbox',
                                           'data-options': "multiline:true"}),
        }


class RefundReviewForm(forms.ModelForm):
    submit_notes = forms.CharField(max_length=200,help_text=u'',label=u'提交备注',disabled=True,widget=forms.Textarea(attrs={'style': 'width:300px;height:100px;','readonly':True}))
    student = forms.ModelChoiceField(queryset=Student.objects.all(),disabled=True,label=u'学生',widget=forms.TextInput(attrs={'readonly':True}))
    class Meta:
        model = Absence
        fields = ('student','days','balance','submit_notes','review_notes')
        widgets = {
            'days':forms.TextInput(attrs={'disabled':True}),
            'balance':forms.TextInput(attrs={'disabled':True}),
            'review_notes': forms.Textarea(
                attrs={'style': 'width:300px;height:100px;','class': 'easyui-textbox',
                       'data-options': "multiline:true"}),
        }

