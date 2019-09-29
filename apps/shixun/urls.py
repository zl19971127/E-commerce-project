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

from apps.shixun import views

urlpatterns = [

    #  忘记密码的操作
    url(r"^find_password/$", views.FindPassword.as_view(),name="findpassword" ),

    # 验证用户是否存在
    url(r"^accounts/(?P<username>[a-zA-Z0-9_-]{5,20})/sms/token/$", views.Account.as_view(),name="account" ),

    # 获取短信验证码
    url(r"^find_password_sms_codes/(?P<mobile>1[3-9]\d{9})/$", views.SmsCodes.as_view(),name="smscodes" ),

    # 提交
    url(r"^accounts/(?P<mobile>[a-zA-Z0-9_-]{5,20})/password/token/$", views.SmsAccouts.as_view(),name="smsaccouts" ),

    # 重置密码
    url(r"^users/(?P<user_id>\d+)/new_password/$", views.UsersNewpassword.as_view(),name="usersnewpassword" ),


    # 　微博登录
    url(r"^sina/login/$", views.SianLogin.as_view(),name="sianlogin" ),


    # 微博绑定页面显示
    url(r"^sina_callback/$", views.SianCallback.as_view(),name="siancallback" ),

    # 绑定用户提交
    url(r"^oauth/sina/user/$", views.OauthSinaUser.as_view(),name="oauthsinauser" ),


    # 我的订单
    url(r"^orders/info/(?P<page_num>\d+)/$", views.OrderInfoa.as_view(),name="orderinfo" ),


    # 评价订单商品
    url(r"^orders/comment/$", views.OrderComment.as_view(),name="ordercomment" ),


    # 详情页展示评价信息
    url(r"^comments/(?P<sku_id>\d+)/$", views.Comments.as_view(),name="comments" ),





]
