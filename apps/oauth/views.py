
from django import http
from django.contrib.auth import login
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings

from apps.oauth.models import OAuthQQUser
from apps.users.models import User
from meiduo_mall.settings.dev import logger
from utils.response_code import RETCODE


class QQAuthURLView(View):
    def get(self,request):
        # next = request.GET.get(next)

        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI, state=None)
        login_url = oauth.get_qq_url()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url':login_url})


# http://www.meiduo.site:8000/oauth_callback?code=B4DAD66CAF6FFD1E420FF9189B28493E&state=None
class QQAuthUserView(View):
    def get(self,request):
        code = request.GET.get("code")
        if not code:
            return http.HttpResponseForbidden('缺少code')
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI, state=None)
        try:
            accss_token = oauth.get_access_token(code)
            openid = oauth.get_open_id(accss_token)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('OAuth2.0认证失败')
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except Exception as e:
            #
            context = {"openid":openid}
            return render(request, 'oauth_callback.html',context)
        else:
            qq_user = oauth_user.user
            login(request, qq_user)

            # 重定向到主页
            response = redirect(reverse('users:index'))

            # 登录时用户名写入到cookie，有效期15天
            response.set_cookie('username', qq_user.username, max_age=3600 * 24 * 15)

            return response


    def post(self,request):
        # 接受参数
        mobile = request.POST.get("mobile")
        pwd = request.POST.get("password")
        sms_code_client = request.POST.get("sms_code")
        openid = request.POST.get('openid')
        print(openid)

        # 校验
        # 保存注册数据
        try:
            # 判断数据库中是否存在该用户
            user = User.objects.get(mobile=mobile)
        except Exception as e:
            # 如果用户不存在就新建用户
            user = User.objects.create_user(username=mobile,password=pwd,mobile=mobile,)
        else:
            if not user.check_password(pwd):
                return render(request, 'oauth_callback.html', {'account_errmsg': '用户名或密码错误'})
            # 绑定ｏｐｅｎｉｄ
            try:
                OAuthQQUser.objects.create(openid=openid,user=user)
            except Exception as e:
                return render(request, 'oauth_callback.html', {'qq_login_errmsg': 'QQ登录失败'})

            # 保持登陆状态
            login(request,user)

            # 跳转首页
            response = redirect(reverse("users:index"))
            response.set_cookie("username",user.username,max_age=3600*12*14)

            # 合并购物车
            from apps.carts.utils import merge_cart_cookie_to_redis
            merge_cart_cookie_to_redis(request, response)
            return response









