from django.shortcuts import render,HttpResponse,reverse,redirect
from django.conf import settings
from app01.forms import RegisterForm,UserinfoForm
from django.views import View
from django.contrib import auth
from django.db.models import Count
from django.db.models import F
from itsdangerous import JSONWebSignatureSerializer as Serializer
from celery_tasks.tasks import send_register_active_email
from app01 import models
from utils.pager import PageInfo
import json
from django.conf import settings
import os
from bs4 import BeautifulSoup

#登录-注册CBV视图----第一天完成
class Blog(View):

    def get(self,request):
        form_obj = RegisterForm()

        # 判断是否记住了用户名
        if 'username' in request.COOKIES:
            username=request.COOKIES.get('username')
            checked='checked'
        else:
            username=''
            checked=''
        return render(request, 'blog.html', {'form_obj': form_obj,'username':username,'checked':checked})

    def post(self,request):
        #如果接收自注册url的请求
        if request.path_info==reverse('register'):
            form_obj = RegisterForm(request.POST)
            if form_obj.is_valid():
                #如果验证通过
                user=models.UserInfo.objects.create_user(**form_obj.cleaned_data)
                user.is_active=0
                user.save()

                #加密用户信息
                serializer = Serializer(settings.SECRET_KEY, '3600')
                info = {'confirm': user.nid}
                token = serializer.dumps(info)
                token = token.decode('utf-8')

                send_register_active_email(user.email,user.username,token)

                # return redirect(reverse('login'))#返回到login页面
                return HttpResponse('您已注册成功QAQ，已发送激活邮件到您的注册邮箱，为了网络安全及防止恶意注册账户，请通过链接登录账号')
            else:
                return render(request,'blog.html',{'form_obj':form_obj})
        else:
            form_obj=RegisterForm()
            #取出数据
            username=request.POST.get('username')
            password=request.POST.get('password')
            remember=request.POST.get('remember')

            # 效验数据
            if not all([username,password]):
                return render(request,'blog.html',{'errmsg':'输入数据不完整','form_obj':form_obj})

            user_test = models.UserInfo.objects.filter(username=username).first()
            if not user_test.is_active:
                return HttpResponse('小样，没激活就想登录，你个机器人，请通过注册邮箱激活链接登录吧')

            #业务处理：验证用户存在
            user=auth.authenticate(request,username=username,password=password)
            if user is not None:
                #如果验证通过,记录登录状态,返回首页
                auth.login(request,user)
                response=redirect(reverse('index'))

                #判断是否记住用户名
                if remember=='on':
                    #记住用户名
                    response.set_cookie('username',username,max_age=60*60*12*7)
                else:
                    response.delete_cookie('username')

                return response
            else:
                return render(request,'blog.html',{'errmsg':'用户名或密码错误','form_obj':form_obj})

#激活账户
def active(request,*args,**kwargs):
    # 进行解密，获取要激活的用户信息
    serializer = Serializer(settings.SECRET_KEY, '3600')
    try:
        info = serializer.loads(args[0])
        # 获取待激活用户的id
        user_id = info['confirm']
        # 根据id获取用户信息
        user = models.UserInfo.objects.get(nid=user_id)
        user.is_active = 1
        user.save()
        # 跳转到登录界面
        return redirect(reverse('login'))
    except Exception:
        # 如果激活时间已过期
        return HttpResponse('激活链接已过期')

#注销
def logout(request):
    auth.logout(request)
    return redirect(reverse('login'))

#首页CBV视图
class Index(View):
    def get(self,request):
        '''自定义分页，限制显示的条数'''
        count=models.Article.objects.all().count()
        page_info=PageInfo(request.GET.get('page'),count,5,request.path_info)
        article_list=models.Article.objects.all()[page_info.start():page_info.end()]

        #查询所有的分类，标签各个数量
        category_obj = models.Category.objects.values('nid').annotate(a=Count('article__title')).values('title', 'a')
        tag_obj = models.Tag.objects.values('nid').annotate(a=Count('title')).values('title', 'a')

        context={
            'article_list': article_list,
            'page_info':page_info,
            'category_obj':category_obj,
            'tag_obj':tag_obj,
        }
        return render(request,'index.html',context)

#个人博客首页
def home(request,username):
    #去userinfo把用户对象取出来,找出对应blog站点
    user=models.UserInfo.objects.filter(username=username).first()
    blog=user.blog

    #我的文章列表
    article_list=models.Article.objects.filter(user=user).all()

    return render(request,'home.html',{'blog':blog,
                                       'article_list':article_list,
                                       'username':username
                                       })

#文章详情
def article_detail(request,username,pk):
    '''
    :param request:   request请求
    :param username:    这篇文章的用户
    :param pk:          这篇文章的id
    :return:
    '''
    # 去userinfo把用户对象取出来,找出对应blog站点
    user = models.UserInfo.objects.filter(username=username).first()
    blog = user.blog
    article_obj=models.Article.objects.filter(pk=pk).first()

    #取出这篇文章的评论
    comment_list=models.Comment.objects.filter(article_id=pk)

    return render(request,'article_detail.html',{
        'article_obj':article_obj,
        'blog':blog,
        'username':username,
        'comment_list':comment_list,
    })

#点赞与踩
def up_down(request):
    print('我调用了吗')
    '''以下三个分别为是否点赞，文章id，登录用户'''
    is_up=json.loads(request.POST.get('is_up'))
    article_id=request.POST.get('article_id')
    user=request.user
    ret={'state':True}
    #捕捉唯一索引错误
    try:
        models.ArticleUpDown.objects.create(user=user,article_id=article_id,is_up=is_up)
        # 文章表中点赞与反对
        if is_up:
            models.Article.objects.filter(pk=article_id).update(up_count=F('up_count') + 1)
        else:
            models.Article.objects.filter(pk=article_id).update(down_count=F('down_count') + 1)
    except Exception as e:
        ret['state']=False
        ret['first_action']=models.ArticleUpDown.objects.filter(user=user,article_id=article_id).first().is_up

    return HttpResponse(json.dumps(ret))

#评论
def comment(request):
    '''拿取评论表需要的数据'''
    article_id=request.POST.get('article_id')
    content=request.POST.get('content')
    pid=request.POST.get('pid')
    user_pk=request.user.pk
    ret={}
    if not pid:
        #如果是根评论
        comment_obj=models.Comment.objects.create(article_id=article_id,content=content,user_id=user_pk)
    else:
        comment_obj = models.Comment.objects.create(article_id=article_id, content=content, user_id=user_pk,parent_comment_id=pid)
    ret['create_time']=comment_obj.create_time.strftime('%Y-%m-%d')
    ret['username']=comment_obj.user.username
    ret['content']=comment_obj.content
    ret['comment_pk']=comment_obj.pk
    return HttpResponse(json.dumps(ret))

#后台编辑器添加文章
def add_article(request):
    if request.method=='GET':
        #做判断进行审核是否有资格发布博客
        user = request.user
        if user.blog==None:
            return HttpResponse('您未获得发布博客的资格，请联系作者给予个人站点空间！')
        '''获取分类表和标签表的数据'''
        category_obj=models.Category.objects.values('nid','title')
        tag_obj=models.Tag.objects.values('title','blog__nid','blog__title').filter(blog__site=user.username).values()

        return render(request,'add_article.html',{'category_obj':category_obj,'tag_obj':tag_obj})
    else:
        '''获取文章标题，内容，类别，标签，当前用户'''
        title=request.POST.get('title')
        article_content=request.POST.get('article_content')
        category_list=request.POST.get('category')
        tag_list=request.POST.getlist('tag')
        user=request.user

        #解析上传文档
        bs=BeautifulSoup(article_content,'html.parser')
        desc=bs.text[0:150]+'...'

        #过滤非法标签
        for tag in bs.find_all():
            if tag.name in ['script','link']:
                tag.decompose()

        article_obj=models.Article.objects.create(title=title,desc=desc,user=user,category_id=category_list)#文章表
        models.ArticleDetail.objects.create(content=str(bs),article=article_obj)#文章详情表
        #添加文章对应标签
        for tag in tag_list:
            models.Article2Tag.objects.create(article_id=article_obj.pk,tag_id=tag)

        return redirect(reverse('index'))

#富文本编辑器上传图片
def upload(request):
    '''获取数据，写入文件，并存放到相应位置,返回给前端文件路径'''
    img_obj=request.FILES.get('upload_img')
    path=os.path.join(settings.MEDIA_ROOT,'add_article_img',img_obj.name)
    with open(path,'wb') as f:
        for line in img_obj:
            f.write(line)

    ret={
        'error':0,
        'url':'/media/add_article_img/%s'%(img_obj.name)
         }

    return HttpResponse(json.dumps(ret))

#修改头像
def crop(request):
    if request.method=='GET':
        avatar_obj=models.UserInfo.objects.filter(username=request.user.username).values('avatar').first()
        return render(request,'crop.html',{'avatar_obj':avatar_obj})
    else:
        #接收数据
        obj=request.FILES.get('file')
        user=request.user

        #判断
        if not all([obj,user]):
            return HttpResponse('请先选择上传文件哟')

        #写入本地
        path=os.path.join(settings.MEDIA_ROOT,'avatars',obj.name)
        with open(path,'wb') as f:
            for line in obj:
                f.write(line)
            f.close()

        #更新用户表的头像字段
        avater_name='avatars/'+obj.name
        user_obj=models.UserInfo.objects.filter(username=user.username).update(avatar=avater_name)
        print(avater_name)

        return redirect(reverse('blog:crop'))

#用户中心
def userinfo(request):
    obj = models.UserInfo.objects.filter(username=request.user.username).first()
    if request.method=='GET':
        form_obj=UserinfoForm(instance=obj)
        return render(request,'userinfo.html',{'form_obj':form_obj})
    else:
        form_obj=UserinfoForm(request.POST,instance=obj)
        return HttpResponse('ok')

def test(request):
    return render(request,'test.html')