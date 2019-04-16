from django import template
from django.urls import reverse
from django.http import QueryDict

register = template.Library()


@register.simple_tag()
def reverse_url(request, name, *args, **kwargs):
    """
    反向解析生成URL, 拼接参数
    :param request: 需要从request.GET中获取QueryDict
    :param name: 获取反向解析的别名
    :param args: 其他位置参数,比如pk
    :param kwargs: 其他关键字参数
    :return:
    """
    # 根据传来的url别名和参数反向解析生成基本URL
    base_url = reverse(name, args=args, kwargs=kwargs)
    # 从当前的URL上获取参数 -->
    params = request.GET.urlencode()
    # print(request.GET)    # # <QueryDict: {'query': [''], 'page': ['3']}>
    # print(request.GET.urlencode())   # query=4&page=3
    if not params:
        return base_url
    return '{}?{}'.format(base_url, params)


@register.simple_tag()
def rev_url(request, name, *args, **kwargs):
    """
     在模板的a标签中调用此标签. 记录当前全url, 跳转到别名所对应的url时,后面携带当前url,以便在新页面提交请求后返回当前页面
    :param request:  请求
    :param name: 别名
    :param args:  位置参数
    :param kwargs: 关键字参数
    :return:
    """
    # 根据别名拿到要跳转到url地址
    base_url = reverse(name, args=args, kwargs=kwargs)
    # print(base_url)   # /crm/edit_customer/6/     # <a href="{% rev_url request 'edit_customer' customer.pk %}">

    # 直接拿到当前的全URL
    url = request.get_full_path()
    # print(url)   # /crm/my_customer/?page=3
    # 携带参数的字典, 将其变为可修改的
    qd = QueryDict(mutable=True)
    # 给字典添加键值对,next对应当前的全url(含参数)地址. 之后如果想要获取原页面的url信息,可以通过QueryDict的next中获取
    qd['next'] = url
    # 返回要跳转的url地址与当前全url(含参数)地址拼接的字符串
    return '{}?{}'.format(base_url, qd.urlencode())
