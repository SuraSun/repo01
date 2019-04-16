"""oldboy_crm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from crm.views import account
from django.shortcuts import HttpResponse

def test(request):
    return HttpResponse('学什么python')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/', account.login, name='login'),
    url(r'^logout/', account.logout, name='logout'),
    url(r'^index/', account.index, name='index'),
    url(r'^reg/', account.reg, name='reg'),
    url(r'^crm/', include('crm.urls')),
    url(r'^test/', test),
]
