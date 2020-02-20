from django import template
from app01 import models
from django.db.models import Count

register=template.Library()

@register.inclusion_tag('left_menu.html')
#显示左侧菜单
def get_left_menu(username):
    # 去userinfo把用户对象取出来,找出对应blog站点
    user = models.UserInfo.objects.filter(username=username).first()
    blog = user.blog
    # 我的文章分类，每个分类下的文章个数
    nid = models.UserInfo.objects.get(username=username).nid
    category_list = models.Category.objects.filter(article__user__nid=nid).annotate(a=Count('article')).values('title',
                                                                                                               'a')

    # 统计标签，并计算出每个标签下的文章数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(a=Count('article')).values('title', 'a')

    # 日期归档
    archive_list = models.Article.objects.filter(user=user).extra(
        select={'archive_ym': "date_format(create_time,'%%Y-%%m')"}
    ).values('archive_ym').annotate(a=Count('nid')).values('archive_ym', 'a')
    return {
        'category_list':category_list,
        'tag_list':tag_list,
        'archive_list':archive_list
    }