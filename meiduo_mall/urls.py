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
from django.conf.urls import url, include
# from django.contrib import admin

urlpatterns = [
    # url(r'^admin/', admin.site.urls),

    url(r"^users/", include("apps.users.urls", namespace="users")),

    url(r"^",include("apps.oauth.urls", namespace="qqlogin")),


    url(r"^",include("apps.areas.urls", namespace="areas")),


    url(r"^",include("apps.goods.urls", namespace="goods")),


    url(r"^",include("apps.carts.urls", namespace="carts")),


    url(r"^",include("apps.orders.urls", namespace="orders")),


    url(r"^",include("apps.payment.urls", namespace="payment")),

    #　　搜索
    url(r'^search/', include('haystack.urls')),

    url(r'^', include('apps.shixun.urls',namespace="shixun")),


    # ｍｅｉｄｕｏ后台实现
    url(r"^meiduo_admin/",include("apps.meiduo_admin.urls",namespace="meiduo_admin"))


]
