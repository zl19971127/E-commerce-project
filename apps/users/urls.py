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

from apps.users import views

urlpatterns = [

    # 注册页的路由
    url(r"^register/$", views.Register.as_view(),name="register" ),

    # 首页的路由
    url(r"^index/$", views.Index.as_view(),name="index"),

    # 判断用户名是否重复的路由
    url(r"^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$", views.Userconut.as_view(),name="usercount" ),

    # 判断手机号是否重复的路由
    url(r"^mobiles/(?P<mobile>[a-zA-Z0-9_-]{5,20})/count/$", views.Mobilecount.as_view(),name="mobilecount" ),

    # 图形验证码的路由
    url(r"^image_codes/(?P<uuid>[\w-]+)/$", views.Captcha.as_view(),name="captcha" ),


    # 手机验证码判断的路由
    url(r"^sms_codes/(?P<mobile>1[3-9]\d{9})/$", views.Sms_codes.as_view(),name="smacodes" ),


    # 登陆页面路由
    url(r"^login/$", views.Login.as_view(),name="login" ),


    #　退出路由
    url(r"^logout/$", views.Logout.as_view(),name="logout" ),


    # 用户中心
    url(r"^info/$", views.Info.as_view(),name="info" ),

    # 邮件发送
    url(r"^emails/$", views.Emails.as_view(), name="emails"),


    # 邮箱验证
    url(r"^emails/verification/$", views.Emailsverification.as_view(), name="emailsver"),


    # 修改密码
    url(r"^password/$", views.ChangePassword.as_view(), name="password"),

    # 保存用户的浏览记录
    url(r"^browse_histories/$", views.BrowseHistories.as_view(), name="brow"),



    # 如果路由是：www.meiduo.site:8000 就改成/users/index/

]
