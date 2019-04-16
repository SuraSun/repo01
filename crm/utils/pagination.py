class Pagination:

    def __init__(self, page, all_count, params, per_num=15, max_show=11):
        """

        :param page:  当前页码
        :param all_count:  总共多少条数据
        :param params:  request.GET.copy() get请求数据这个字典的深拷贝字典, 可进行修改, 也就是url后面的参数
        :param per_num:  每页显示多少条数据
        :param max_show:  最多显示多少页
        """
        try:
            page = int(page)
            if page <= 0:
                page = 1
        except Exception as e:
            page = 1

        self.params = params  # 条件
        self.page = page
        self.all_count = all_count
        self.per_num = per_num
        self.max_show = max_show
        # 总页码数
        self.page_num, more = divmod(all_count, per_num)
        if more:
            self.page_num += 1
        # 最多显示页码数
        half_show = max_show // 2

        # 总页码数不够最大显示页码数
        if self.page_num < max_show:
            # 显示页码从1开始
            self.page_start = 1
            # 终止页码是最后一页
            self.page_end = self.page_num
        else:
            # 能显示超过最大显示页码数
            # 左边页码数量不足显示页码总数的一半
            if page <= half_show:
                # 处理左边的极值, 从第一页显示
                self.page_start = 1
                # 显示最多能显示的页码数
                self.page_end = max_show
                # 如果当前页数+显示页码总数的一半超过总共的页数
            elif page + half_show > self.page_num:
                # 处理右边的极值, 保证显示的是最多显示页码数
                self.page_start = self.page_num - max_show + 1
                # 保证最后一页显示的是最大页码
                self.page_end = self.page_num
            else:
                # 正常情况
                # 起始为当前页-显示页码总数的一半
                self.page_start = page - half_show
                # 终止为当前页码+显示页码总数的一半
                self.page_end = page + half_show

    @property
    def start(self):   # 切片起始数据索引
        return (self.page - 1) * self.per_num

    @property
    def end(self):   # 切片终止索引
        return self.page * self.per_num

    # 此处是返回给模板的分页html代码段
    @property
    def page_html(self):
        # 显示的页码标签一开始是空列表,等待往里面添加页码标签, 之后会通过join方法把列表转化成字符串,通过safe过滤器在页面中渲染出所有标签
        li_list = []

        # 上一页
        # 如果当前页已经是第一页了,则禁用上一页
        if self.page == 1:
            li_list.append('<li class="disabled" ><a> << </a></li>')
        else:
            # 如果当前页不是第一页, 上一页页码数等于当前页码数-1
            # params = request.GET.copy(), 因为request.GET是一个不可变的QueryDict.里面以键值对的形式携带了url参数. 在深拷贝的这个字典中加入页码键值对, 组成查询条件和页码组合参数.
            # 此处传过来的params字典里可能包含query搜索条件, 此时增加键值对,在字典中添加页码参数. 此处添加上一页的页码
            self.params['page'] = self.page - 1  # self.params.urlencode() —— 》 query=1&page=1
            # 利用.urlencode()方法将字典转化为字符串,放到a标签的url地址中,点击a标签则可获取query查询条件以及page页码信息.  query=1&page=1
            li_list.append('<li ><a href="?{}"> << </a></li>'.format(self.params.urlencode()))

        # 此处获取起始页和最大显示页
        for i in range(self.page_start, self.page_end + 1):
            # 把页码信息交给params, 增加每个页码a标签的锚点参数信息
            self.params['page'] = i  # self.params.urlencode()  query=1&page=  i
            # 如果当前页等于此时循环到的页码数
            if self.page == i:
                # 增加类名active, 此标签为选中状态. 把参数和当前页码信息格式化到标签字符串中, 添加到列表
                li_list.append('<li class="active"><a href="?{0}">{1}</a></li>'.format(self.params.urlencode(), i))
            else:
                # 此处非当前页的标签字符串,没添加类名,不是选中状态, 格式化后也添加到列表中
                li_list.append('<li><a href="?{0}">{1}</a></li>'.format(self.params.urlencode(), i))

        # 下一页
        self.params['page'] = self.page + 1  # query=1&page=3
        #  如果当前页是最大页码
        if self.page == self.page_num:
            # 下一页标签禁用
            li_list.append('<li class="disabled" ><a> >> </a></li>')
        else:
            # 如果当前页不是最大页码,可以点下一页
            li_list.append('<li ><a href="?{}"> >> </a></li>'.format(self.params.urlencode()))

        # 把列表中的标签拼接成字符串, 发送给模板,通过过滤器safe渲染到页面中, 形成分页
        return ''.join(li_list)
