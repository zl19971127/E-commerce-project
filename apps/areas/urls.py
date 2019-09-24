"""meiduo_mall URL Configuration

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
from django.conf.urls import url

from apps.areas import views

urlpatterns = [

    # 收货地址路径跳转
    url(r"^address/$", views.Addresses.as_view(),name="address" ),

    # 收货地址增加
    url(r"^addresses/create/$", views.AddressCreate.as_view(), name="addresscreate"),

    # 三级联动
    url(r"^areas/$", views.AreasView.as_view(), name="areas"),

    url(r"^$", views.ABC.as_view())

]
