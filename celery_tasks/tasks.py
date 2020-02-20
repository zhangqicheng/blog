from celery import Celery
import time
from django.conf import settings
from django.core.mail import send_mail
#实例化celery
apps=Celery('celery_tasks.tasks',
            broker='redis://127.0.0.1:6379/1',
            backend='redis://127.0.0.1:6379/2'
            )

#创建任务函数
@apps.task
def send_register_active_email(to_email,username,token):
    '''发送激活邮件'''
    # 组织邮件信息
    subject = '张启程开发----博客欢迎您'
    html_message = '<h1>%s,欢迎加入博客站点</h1><a href="http://127.0.0.1:8000/active/%s">请点击以下链接激活会员:http://127.0.0.1:8000/active/%s</a>' % (
        username, token, token)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [to_email]
    send_mail(subject, message='正文', from_email=from_email, recipient_list=recipient_list, html_message=html_message)
    time.sleep(5)