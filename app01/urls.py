from django.contrib import admin
from django.urls import path,include,re_path
from app01 import views
from django.views.static import serve
from django.conf import settings
from django.conf.urls import url

urlpatterns = [
    path('test/',views.test),
    path('up_down/',views.up_down,name='up_down'),
    path('comment/',views.comment,name='comment'),
    path('backend/add_article/',views.add_article,name='add_article'),
    path('upload/',views.upload),
    path('avatar/crop/',views.crop,name='crop'),         #修改头像
    path('user_info/',views.userinfo,name='userinfo'),   #个人中心
    re_path('(\w+)/$',views.home,name='home'),
    re_path('(\w+)/article/(\d+).html$',views.article_detail,name='article_detail'),
]
