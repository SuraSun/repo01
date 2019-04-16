from django.shortcuts import render, HttpResponse, redirect, reverse
from crm import models
from crm.forms import RegForm
import hashlib


def index(request):
    return HttpResponse('index')


def login(request):
    err_msg = ''
    if request.method == 'POST':

        # 获取提交的数据
        user = request.POST.get('user')
        pwd = request.POST.get('pwd')

        # 加密
        md5 = hashlib.md5()
        md5.update(pwd.encode('utf-8'))
        pwd = md5.hexdigest()
        # 查询
        obj = models.UserProfile.objects.filter(username=user, password=pwd, is_active=True).first()
        if obj:
            # 认证成功,保存用户的id在session中
            request.session['user_id'] = obj.pk
            # 跳转到首页
            return redirect(reverse('customer_list'))
        err_msg = '用户名或密码错误'

    return render(request, 'login.html', {'err_msg': err_msg})


def logout(request):
    request.session.flush()
    return redirect(reverse('login'))


def reg(request):
    form_obj = RegForm()
    if request.method == 'POST':
        form_obj = RegForm(request.POST)
        if form_obj.is_valid():  # 校验数据是否符合UserProfile中字段的格式要求
            # print(form_obj.cleaned_data)
            # 写入到数据库中
            # form_obj.cleaned_data.pop('re_password')
            # obj = models.UserProfile.objects.create(**form_obj.cleaned_data)
            # print(obj)
            form_obj.save()
            # print(form_obj.cleaned_data)  # 字典 字段名对应数据
            user_obj = models.UserProfile.objects.filter(username=form_obj.cleaned_data['username']).first()
            request.session['user_id'] = user_obj.pk
            # print(request.session['user_id'])
            return redirect(reverse('index'))

    return render(request, 'reg.html', {'form_obj': form_obj})

