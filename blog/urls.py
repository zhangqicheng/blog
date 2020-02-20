"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include,re_path
from app01 import views
from django.views.static import serve
from django.conf import settings
from django.conf.urls import url

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('active/(.*)/$',views.active),
    path('tinymce/',include('tinymce.urls')),#富文本编辑
    path('login/',views.Blog.as_view(),name='login'),
    path('logout/',views.logout,name='logout'),
    path('register/',views.Blog.as_view(),name='register'),
    #首页
    path('index/',views.Index.as_view(),name='index'),
    #home
    path('blog/',include(('app01.urls','app01'),namespace='blog')),#用户模块



    # media相关的路由设置
    url(r'^media/(?P<path>.*)$', serve, {"document_root": settings.MEDIA_ROOT}),
]