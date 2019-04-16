from django import forms
from crm import models
from django.core.exceptions import ValidationError
import hashlib


class BootstrapForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


# 注册form
class RegForm(BootstrapForm):
    password = forms.CharField(widget=forms.PasswordInput(), label='密码', min_length=6)  # 会把默认生成的字段覆盖掉
    re_password = forms.CharField(widget=forms.PasswordInput(), label='确认密码', min_length=6)

    class Meta:
        # 对应UserProfile表的字段信息
        model = models.UserProfile
        fields = "__all__"  # 从用户表中拿到所有字段,不用再自己写字段啦. 但是用户表中没有确认密码字段,所以这个自己写一下~
        # fields = ['username', 'password']
        exclude = ['is_active']  # 排除某些字段

        labels = {
            'username': '用户名',
            'password': '密码',
            # 're_password': '确认密码', 改不了label显示名称
            'department': '部门',
        }

        widgets = {
            # 'password': forms.PasswordInput(attrs={'class': 'form-control'})   # 设置标签属性. 上面写了password, 下面的就无效了
        }

        error_messages = {
            'username': {
                'required': '不能为空',
                'invalid': '格式错误',
            }
        }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # print(self.fields)  # 拿到有序列表,里面字段名:对象
    #     # 循环自动加类名, 不用手动添加
    #     for field in self.fields.values():
    #         field.widget.attrs.update({'class': 'form-control'})  # 同字典. 更新标签属性,其他的属性不影响

    # 局部钩子
    # 当form组件自带的校验规则不能满足需求,需要我们自行设计校验规则,用钩子.
    # 导入模块from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
    # 要求密码不能是纯数字
    def clean_password(self):
        val = self.cleaned_data.get('password')  # 获取输入的密码

        if not val.isdigit():  # 判断是不是数字类型
            return val
        else:
            raise ValidationError('密码不能是纯数字')

    '''
    注意：

    clean_name  这个名字是有含义的，不能随便定义。name表示UserForm类的属性。clean表示校验
    
    val 表示用户输入的用户名
    
    val.isdigit() 表示判断输入的是否为数字，必须return 一个值
    
    raise 表示主动报错，必须接ValidationError。
    '''

    '''
    注意：

    is_valid执行时，才会执行校验。
    
    这里有2层校验。第一层校验是UserForm定义的那些属性，比如判断字符串或者数字的。
    
    第二次校验是clean_属性名 定义的这些方法。只有通过第一层校验时，才会进入第二层校验。
    
    不论式第一层还是第二层，通过校验后，将key_value放到 cleaned_data容器里面。不通过校验时，将key-value放到errors容器里面
    '''

    ### 全局钩子

    # def clean(self):
    """
    Hook for doing any extra form-wide cleaning after Field.clean() has been
    called on every field. Any ValidationError raised by this method will
    not be associated with a particular field; it will have a special-case
    association with the field named '__all__'.
        """
    '''
    这是一个钩子, 在所有字段都执行了Field.clean()方法后, 它会再次对表单范围内进行清洗.此方法抛出的任何校验异常
    都不会和某一字段有所关联. 这个异常将和名为"__all__" 的字段产生特殊关联.
    '''

    # return self.cleaned_data

    # 全局钩子
    def clean(self):
        pwd = self.cleaned_data.get('password', '')
        r_pwd = self.cleaned_data.get('re_password')

        if pwd and pwd == r_pwd:
            # 对密码加密
            md5 = hashlib.md5()
            md5.update(pwd.encode('utf-8'))
            pwd = md5.hexdigest()
            self.cleaned_data['password'] = pwd
            return self.cleaned_data  # 固定写法,不能变

        self.add_error('re_password', '两次密码不一致')  # 把错误信息添加到字段
        raise ValidationError('两次密码不一致')  # 将异常添加到__all__


# 客户form
class CustomerForm(BootstrapForm):
    class Meta:
        model = models.Customer
        fields = '__all__'

        error_messages = {
            'qq': {
                'required': '不能为空',
                'invalid': '格式错误',
            },
            'course': {
                'required': '不能为空',
                'invalid': '格式错误',
            },
            'class_list': {
                'required': '不能为空',
                'invalid': '格式错误',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].widget.attrs = {}


# 跟进记录form
class ConsultForm(BootstrapForm):
    class Meta:
        model = models.ConsultRecord
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 去除delete_status字段标签的class中form-control属性,美化页面
        self.fields['delete_status'].widget.attrs.pop('class')

        # 当前登录的用户(销售)
        # print(list(self.fields['customer'].choices)) # [('', '---------'), (1, '小明 QQ:11212424')]
        # print(self.instance)
        # print(self.instance.consultant)

        # 拿到当前销售的客户id和名字
        customer_choices = [(i.pk, str(i)) for i in self.instance.consultant.customers.all()]
        # 设置初始选项显示空
        customer_choices.insert(0, ('', '---------'))

        # 让customer字段只能选择当前销售用户自己的客户
        self.fields['customer'].choices = customer_choices
        # 让consultant字段只能显示当前销售自己
        self.fields['consultant'].choices = [(self.instance.consultant.pk, self.instance.consultant.name)]


# 报名记录

class EnrollmentForm(BootstrapForm):
    class Meta:
        model = models.Enrollment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['delete_status'].widget.attrs.pop('class')
        self.fields['contract_agreed'].widget.attrs.pop('class')
        self.fields['contract_approved'].widget.attrs.pop('class')

        # 限制可选客户是当前客户
        self.fields['customer'].choices = [(self.instance.customer.pk, str(self.instance.customer))]
        # 限制可选班级是客户信息中已报班级
        # print(self.instance)
        self.fields['enrollment_class'].choices = [(i.pk, str(i)) for i in self.instance.customer.class_list.all()]


# 班级form
class ClassForm(BootstrapForm):
    class Meta:
        model = models.ClassList
        fields = '__all__'


class CourseRecordForm(BootstrapForm):
    class Meta:
        model = models.CourseRecord
        fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # 限制班级是当前的班级
    #     self.fields['re_class'].choices = [(self.instance.re_classs_id, str(self.instance.re_class))]


class StudyRecordForm(BootstrapForm):
    class Meta:
        model = models.StudyRecord
        fields = '__all__'
