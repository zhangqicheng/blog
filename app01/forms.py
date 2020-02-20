from django import forms
from app01 import models

#注册form
class RegisterForm(forms.ModelForm):
    email=forms.CharField(
        label='邮箱',
        widget=forms.widgets.TextInput(),
        error_messages={
            'required':'邮箱不能为空',
            'invalid': '邮箱格式不正确,请输入:xxx@xx.com格式'
        }
    )
    password=forms.CharField(
        widget=forms.widgets.PasswordInput(attrs={'placeholder':'密码'}),
        error_messages={'required':'密码不能为空'}
    )
    class Meta:
        model=models.UserInfo
        fields=['username','password','email','phone']
        error_messages={
            'username':{'required':'用户名不能为空'},
            'phone':{'required':'电话不能为空'}
        }

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['username'].widget.attrs={'placeholder':'用户名','name':'username'}
        self.fields['email'].widget.attrs = {'placeholder': '邮箱xxx@xx.com格式'}
        self.fields['phone'].widget.attrs = {'placeholder': '电话'}

#用户信息form
class UserinfoForm(forms.ModelForm):
    class Meta:
        model=models.UserInfo
        fields=['username','phone','avatar','blog']
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['blog'].widget.attrs={'disabled':"disabled"}


