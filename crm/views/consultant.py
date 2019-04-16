from django.shortcuts import render, HttpResponse, redirect, reverse
from crm import models
from crm.forms import CustomerForm, ConsultForm, EnrollmentForm
from django.views import View
from django.db.models import Q
from crm.utils.pagination import Pagination
from crm.utils.url import rev_url
from oldboy_crm import settings
from django.db import transaction


# 展示客户 FBV
def customer_list(request):
    # 获取数据
    if request.path_info == reverse('customer_list'):
        # 公户
        all_customers = models.Customer.objects.filter(consultant__isnull=True)
    else:
        # 私户
        all_customers = models.Customer.objects.filter(consultant=request.account)
    return render(request, 'consultant/customer_list.html', {'all_customers': all_customers})


# 展示客户 CBV
class CustomerList(View):

    def get(self, request):
        # Q查询的第一种写法
        # query = request.GET.get('query', '')

        # q = Q()
        # q.connector = 'OR'  # 连接条件默认是AND
        # 里面放查询条件
        # q.children.append(Q(qq__contains=query))  # 里面放元组
        # q.children.append(Q(name__contains=query))

        #  Q(('qq__contains', query))    Q(qq__contains=query)

        q = self.search(['qq', 'name'])

        # 公户
        if request.path_info == reverse('customer_list'):
            public = 1
            all_customers = models.Customer.objects.filter(q, consultant__isnull=True)
            # all_customers = models.Customer.objects.filter(Q(qq__contains=query)|Q(name__contains=query), consultant__isnull=True, )
        else:
            # 私户
            public = 0
            all_customers = models.Customer.objects.filter(q, consultant=request.account)

        # 要求传参 Pagination(page, all_count, params, per_num=15, max_show=11),
        # 此处request.GET.get('page', '1') 获取页码数, 获取不到默认值是1,
        pager = Pagination(request.GET.get('page', '1'), all_customers.count(), request.GET.copy(), 2)

        return render(request, 'consultant/customer_list.html', {'all_customers': all_customers[pager.start: pager.end],
                                                                 'page_html': pager.page_html, 'public': public})

    def post(self, request):
        action = request.POST.get('action')

        if not hasattr(self, action):
            return HttpResponse('非法操作')

        res = getattr(self, action)()
        # 如果操作中有返回值，直接返回res
        if res:
            return res

        return self.get(request)

    def multi_private(self):
        # 公户变私户
        ids = self.request.POST.getlist('id')

        # 给每个销售限制客户数量, 申请转为私户的时候数量不能超限. 当前有的私户+ 申请的数量>最大值,不允许
        # if models.Customer.objects.filter(consultant=self.request.account).count() + len(ids) > settings.MAX_CUSTOMER_NUM:
        if self.request.account.customers.all().count() + len(ids) > settings.MAX_CUSTOMER_NUM:
            return HttpResponse('客户数量超限(最大限制{}), 不能太贪心了哦~'.format(settings.MAX_CUSTOMER_NUM))

        # 事务
        with transaction.atomic():
            # 查询出数据加锁
            queryset = models.Customer.objects.filter(id__in=ids, consultant__isnull=True).select_for_update()  # 加行级锁

            # 如果此时勾选的这些客户没有被别人转成私户, 所勾选的id数量和查询到的公户数量相等, 则转化为私户
            if len(ids) == queryset.count():
                queryset.update(consultant=self.request.account)
                return

            return HttpResponse('你的手速太慢了, 已经被别人抢走了~')



        # 方式一  正向查询好理解
        # models.Customer.objects.filter(id__in=ids).update(consultant=self.request.account)

        # 方式二  关系管理反向查询, 将元组打散
        # self.request.account.customers.add(*models.Customer.objects.filter(id__in=ids))

    # 转成公户
    def multi_public(self):
        ids = self.request.POST.getlist('id')
        # 方式一
        # models.Customer.objects.filter(id__in=ids).update(consultant=None)

        # 方式二
        self.request.account.customers.remove(*models.Customer.objects.filter(id__in=ids))

    def multi_delete(self):
        ids = self.request.POST.getlist('id')

        models.Customer.objects.filter(id__in=ids).delete()

    def search(self, query_list):
        query = self.request.GET.get('query', '')
        # Q(Q(qq__contains=query) | Q(name__contains=query))
        q = Q()
        q.connector = 'OR'  # 默认是AND

        #  Q(('qq__contains', query))    Q(qq__contains=query)
        for i in query_list:
            q.children.append(Q(('{}__contains'.format(i), query)))

        return q


# 增加客户
def add_customer(request):
    # 创建一个空的Form对象
    form_obj = CustomerForm()
    # 接收发送的POST请求数据
    if request.method == 'POST':
        # 创建一个包含提交数据的form对象
        form_obj = CustomerForm(request.POST)
        # 保存数据
        form_obj.save()
        return redirect(reverse('customer_list'))

    return render(request, 'consultant/add_customer.html', {'form_obj': form_obj})


# 编辑客户
def edit_customer(request, edit_id):
    # 查询出要编辑的客户对象
    obj = models.Customer.objects.filter(pk=edit_id).first()
    form_obj = CustomerForm(instance=obj)
    if request.method == 'POST':
        form_obj = CustomerForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()

            return redirect(reverse('customer_list'))

    return render(request, 'consultant/edit_customer.html', {'form_obj': form_obj})


# 新增和编辑客户
def modify_customer(request, edit_id=None):
    # 通过id获取对象
    obj = models.Customer.objects.filter(pk=edit_id).first()
    # 获取form对象, 发送给模板渲染,如果获取的是none,相当于新增
    form_obj = CustomerForm(instance=obj)
    # 接收到POST请求数据
    if request.method == 'POST':
        # 把POST请求的数据替换原来的数据. 如果原来的对象是None, 相当于新增
        form_obj = CustomerForm(request.POST, instance=obj)
        # 通过校验
        if form_obj.is_valid():
            form_obj.save()  # 没有instance新增,有instance做修改
            return redirect(rev_url(request, 'customer_list'))

    return render(request, 'consultant/modify_customer.html', {'form_obj': form_obj, 'edit_id': edit_id})


# 跟进记录展示
class ConsultList(View):

    def get(self, request, customer_id):
        # 获取当前销售的所有跟进记录
        if customer_id == '0':
            my_consults = models.ConsultRecord.objects.filter(consultant=request.account)
        else:
            my_consults = models.ConsultRecord.objects.filter(consultant=request.account, customer_id=customer_id)

        return render(request, 'consultant/consult_list.html', {'my_consults': my_consults})


# 增加跟进记录
def add_consult(request):
    # 实例化一个包含当前销售的跟进记录
    obj = models.ConsultRecord(consultant=request.account)
    # 实例化一个包含当前销售跟进记录的form, 把obj对象交给form
    form_obj = ConsultForm(instance=obj)
    # 处理POST请求
    if request.method == 'POST':
        # 实例化一个带提交参数的Form
        form_obj = ConsultForm(request.POST, instance=obj)
        # 校验数据
        if form_obj.is_valid():
            form_obj.save()  # 新增
            return redirect(reverse('consult_list', args=('0',)))

    return render(request, 'consultant/add_consult.html', {'form_obj': form_obj})


# 修改跟进记录
def edit_consult(request, edit_id):
    obj = models.ConsultRecord.objects.filter(pk=edit_id).first()
    form_obj = ConsultForm(instance=obj)
    if request.method == 'POST':
        form_obj = ConsultForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('consult_list', args=('0',)))

    return render(request, 'consultant/edit_consult.html', {'form_obj': form_obj})


# 报名记录展示
class EnrollmentList(View):
    def get(self, request, customer_id):
        # 获取报名记录
        # 如果customer_id是0就展示全部
        if customer_id == '0':
            all_enrollment = models.Enrollment.objects.all()
        else:
            # 如果传来了具体customer_id,就展示当前id客户的报名记录
            all_enrollment = models.Enrollment.objects.filter(customer_id=customer_id)

        return render(request, 'consultant/enrollment_list.html', {'all_enrollment': all_enrollment})


# 增加,修改报名记录
def enrollment(request, record_id=None, customer_id=None):
    if customer_id:
        # 创建虚拟对象
        obj = models.Enrollment(customer_id=customer_id)
        title = '添加报名记录'
    else:
        obj = models.Enrollment.objects.filter(pk=record_id).first()
        title = '编辑报名记录'

    form_obj = EnrollmentForm(instance=obj)
    if request.method == 'POST':
        form_obj = EnrollmentForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()

            return redirect(reverse('enrollment_list', args=('0',)))
    return render(request, 'consultant/enrollment_form.html', {'form_obj': form_obj, 'title': title})
