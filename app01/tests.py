import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog.settings')

import django
django.setup()

from app01 import models
from django.db.models import Count

# category_obj=models.Category.objects.values('nid').annotate(a=Count('article__title')).values('title','a')
# obj=models.Tag.objects.values('nid').annotate(a=Count('title')).values('title','a')
user=models.UserInfo.objects.filter(username='root').first()
print(user.blog)
