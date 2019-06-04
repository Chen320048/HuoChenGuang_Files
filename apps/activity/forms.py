# coding:utf-8
from django import forms

from models import Activity

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        # fields = '__all__'
        exclude = ('create_user','close_time','status')
        # widgets = {
        #     'image':forms.TextInput(
        #         attrs={'style': 'width:200px','class': 'easyui-filebox easyui-validatebox', 'prompt': u'选择图片文件...', 'buttonText': u'选择',}),
        # }
        widgets = {
            'title':forms.Textarea(
                attrs={'class': 'easyui-textbox','required':True}
            )
        }

class ActivityDeatilForm(forms.Form):
    introduction = forms.CharField(disabled=True)
    detail = forms.CharField(disabled=True)