#封装一个类
class PageInfo(object):
    def __init__(self,current_page,all_count,per_page,base_url,show_page=11):
        """
        :param current_page:  当前页码
        :param all_count:     总的数据个数
        :param per_page:       每页显示的数据个数
        ：base_url:             要显示的url地址
        """
        try:
            self.current_page=int(current_page)
        except:
            self.current_page=1
        self.per_page = per_page
        a,b = divmod(all_count, per_page)
        if b:
            a=a+1
        self.all_pager=a
        self.show_page=show_page
        self.base_url=base_url

    def start(self):
        start=(self.current_page-1)*self.per_page
        return start

    def end(self):
        end=self.current_page*self.per_page
        return end

    def pager(self):
        half=int((self.show_page-1)/2)
        # first=self.current_page-half
        # last=self.current_page+half+1
        page_list=[]
        #如果数据总页数<11
        if self.all_pager<self.show_page:
            first=1
            last=self.all_pager+1
        else:
            #如果当前页<5，则显示1-11页
            if self.current_page<=half:
                first=1
                last=self.show_page+1
            else:
                if self.current_page+half>self.all_pager:
                    first=self.all_pager-self.show_page+1
                    last=self.all_pager+1
                else:
                    first=self.current_page-half
                    last=self.current_page+half+1
        head_page="<li><a href='%s?page=1'>首页</a></li>"%(self.base_url)
        page_list.append(head_page)
        if self.current_page<=1:
            prev="<li><a href='#'>上一页</a></li>"
        else:
            prev="<li><a href='%s?page=%s'>上一页</a></li>"%(self.base_url,self.current_page-1)
        page_list.append(prev)
        for i in range(first,last):
            if (i == self.current_page):
                v = "<li class='active'><a href='%s?page=%s'>%s</a></li>" % (self.base_url,i, i)
            else:
                v = "<li><a href='%s?page=%s'>%s</a></li>" % (self.base_url,i, i)
            page_list.append(v)

        if self.current_page>=self.all_pager:
            nex="<li><a href='#'>下一页</a></li>"
        else:
            nex="<li><a href='%s?page=%s'>下一页</a></li>"%(self.base_url,self.current_page+1)
        page_list.append(nex)
        back_page="<li><a href='%s?page=%s'>尾页</a></li>"%(self.base_url,self.all_pager)
        page_list.append(back_page)
        return page_list