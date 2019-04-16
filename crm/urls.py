from django.conf.urls import url
from crm.views import consultant, teacher

urlpatterns = [
    # 展示公有客户
    # url(r'^customer_list/', views.customer_list, name='customer_list'),
    url(r'^customer_list/', consultant.CustomerList.as_view(), name='customer_list'),
    # 展示私有客户
    url(r'^my_customer/', consultant.CustomerList.as_view(), name='my_customer'),
    # url(r'^my_customer/', views.customer_list, name='my_customer'),
    # 添加客户
    url(r'^add_customer/', consultant.modify_customer, name='add_customer'),
    # 编辑客户
    url(r'^edit_customer/(\d+)/', consultant.modify_customer, name='edit_customer'),

    # 展示跟进记录
    url(r'^consult_list/(?P<customer_id>\d+)/', consultant.ConsultList.as_view(), name='consult_list'),
    # 添加跟进记录
    url(r'^add_consult/', consultant.add_consult, name='add_consult'),
    # 编辑跟进记录
    url(r'^edit_consult/(\d+)/', consultant.edit_consult, name='edit_consult'),

    # 展示报名记录
    url(r'^enrollment_list/(?P<customer_id>\d+)/', consultant.EnrollmentList.as_view(), name='enrollment_list'),
    # 添加报名记录
    url(r'^add_enrollment/(?P<customer_id>\d+)/', consultant.enrollment, name='add_enrollment'),
    # 编辑报名记录
    url(r'^edit_enrollment/(?P<record_id>\d+)/', consultant.enrollment, name='edit_enrollment'),

    ############
    # 展示班级
    url(r'^class_list/', teacher.ClassList.as_view(), name='class_list'),
    # 添加班级
    url(r'^add_class/', teacher.classes, name='add_class'),
    # 编辑 班级
    url(r'^edit_class/(\d+)/', teacher.classes, name='edit_class'),

    # 展示课程记录
    url(r'^course_record_list/(?P<class_id>\d+)/', teacher.CourseRecordList.as_view(), name='course_record_list'),
    # 添加课程记录
    url(r'^add_course_record/(?P<class_id>\d+)/', teacher.course_record, name='add_course_record'),
    # # 编辑 班级
    url(r'^edit_course_record/(?P<course_record_id>\d+)/', teacher.course_record, name='edit_course_record'),
    # 展示学习记录
    url(r'^study_record_list/(?P<course_record_id>\d+)/', teacher.study_record, name='study_record_list'),
]
