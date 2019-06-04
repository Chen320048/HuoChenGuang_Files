# coding:utf-8
from django import forms

from models import *
from apps.account.models import User


class SingleMultipleChoiceField(forms.MultipleChoiceField):
    widget = forms.Select


class KindergartenForm(forms.ModelForm):
    class Meta:
        model = Kindergarten
        fields = '__all__'
        # widgets = {
        #     'name':forms.TextInput
        # }

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ('name','introduction')


class ClassForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ClassForm, self).__init__(*args, **kwargs)
        # self.fields['teacher'] =  添加选择班级教师
    class Meta:
        model = Classes
        fields = ('name','introduction','grade')
        widgets = {
            'grade':forms.HiddenInput(),  # 父级字段隐藏不可选，当添加或者修改子级时弹出的form保证此字段具有值
        }


class StudentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')  # 弹出request
        super(StudentForm, self).__init__(*args, **kwargs)
        user = self.request.user
        kindergarten = Kindergarten.objects.all().values("id")
        if user.type == User.TEACHER:
            teacher = user.bind_teacher
            kindergarten = teacher.classes.grade.kindergarten,
        elif user.type == User.KINDERGARTENOR:
            kindergarten = user.bind_kindergartenor.kindergarten,
        self.fields['classes'] = forms.ModelChoiceField(
            label=u'班级',
            queryset=Classes.objects.filter(grade__kindergarten__in=kindergarten),  # 指定当前幼儿园的班级查询集
            required=True,
            empty_label=''
        )
        self.fields['classes'].widget.attrs['class'] = 'easyui-validatebox'

    class Meta:
        model = Student
        fields = ('name','age','gender','notes','classes')
        widgets = {
            'notes': forms.Textarea(attrs={'style': 'width:300px;height:100px;', 'class': 'easyui-textbox',
                                           'data-options': "multiline:true"}),
        }

