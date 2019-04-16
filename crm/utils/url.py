from django.urls import reverse


def rev_url(request, name, *args, **kwargs):
    """
    通过传来的request获取其参数携带的原页面的url, 如果没有携带,则跳转到指定别名对应的url
    :param request: request请求
    :param name: 要跳转的别名
    :param args: 位置参数
    :param kwargs: 关键字参数
    :return:
    """

    # 获取要跳转的url
    base_url = reverse(name, args=args, kwargs=kwargs)
    # 获取原页面的url
    next_url = request.GET.get('next')
    # 如果有原页面的全url, 则返回原页面
    if next_url:
        return next_url
    # 如果没有原页面url, 则返回当前别名对应的url
    return base_url
