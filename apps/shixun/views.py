import json
import re
from random import randint

from django import http
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from apps.shixun.models import OAuthSinaUser
from apps.users.models import User
from meiduo_mall.settings.dev import logger

# 跳转忘记密码的页面
class FindPassword(View):
    def get(self,request):
        return render(request,"find_password.html")



# 验证用户是否存在
class Account(View):
    def get(self,request,username):
        count = {}
        # 接收参数
        image_code = request.GET.get("image_code")
        uuid = request.GET.get("image_code_id")
        # 校验参数
        # 图形验证码是否正确
        # 链接redis数据库
        client  = get_redis_connection("verify_image_code")
        # 查询redis数据是否存在uuid
        try:
            a = client.get('img_%s' % uuid)
        except:
            return http.JsonResponse({
                "status": 5001,
                "mobile": None,
                "access_token": "abc"
            })

        try:
            client.delete('img_%s' % uuid)
        except Exception as e:
            logger.error(e)
        try:
            if image_code.lower() != a.decode().lower():
               return http.JsonResponse({
            "status": 5001,
            "mobile":None,
            "access_token":"abc"
        })
        except Exception as e:
            logger.error(e)


        # 校验用户是否存在
        try:
            user = User.objects.get(username=username)
        except Exception as e:
            return http.JsonResponse({"status":5004, "mobile":None, "access_token":"abc"})
        else:
            access_token = "abc"
            mobile = user.mobile
            status = 5000

        count = {
            "status": status,
            "mobile":mobile,
            "access_token":access_token
        }

        return  http.JsonResponse(count)


# 短信验证码的发送
class SmsCodes(View):
    def get(self,request,mobile):
        # 接受参数
        access_token =request.GET.get("access_token")
        # 校验参数
        try:
            user = User.objects.get(mobile=mobile)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseForbidden("手机号不存在")

        if access_token != "abc":
            return http.JsonResponse({"status": 5001,'message': "token有误!"})

        # 设计６位随机的短信验证码
        sms_code = randint(100000, 999999)
        # 存到ｒｅｄｉｓ的数据库中
        redis_client = get_redis_connection("sms_code")
        redis_client.setex("sms_%s" % mobile, 300, sms_code)

        # # 使用荣连云发短信
        # from libs.yuntongxun.sms import CCP
        # CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # print("短信验证码是："+str(sms_code))

        # 6. 发短信--容联云
        # from libs.yuntongxun.sms import CCP
        # #                       手机号    6位码 过期时间分钟   短信模板
        # CCP().send_template_sms("mobile", [sms_code, 5], 1)
        print("短信验证码是："+str(sms_code))

        return http.JsonResponse({"status": 5000,'message': "短信发送成功"})


# 提交
class SmsAccouts(View):
    def get(self,request,mobile):
        # 接收参数
        sms_code = request.GET.get("sms_code")

        # 校验参数
        try:
            user = User.objects.get(mobile=mobile)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({"status":5004, "user_id": None, "access_token": None})

        # 判断手机验证码是否正确
        #  链接redis数据库
        client = get_redis_connection("sms_code")
        sms_redis_code = client.get("sms_%s" % mobile)
        if sms_redis_code.decode() != sms_code:
            return http.JsonResponse({"status":5001, "user_id": None, "access_token": None})

        return http.JsonResponse({"status": 5000, "user_id": user.id, "access_token": "abc"})


# 重置密码
class UsersNewpassword(View):
    def post(self,request,user_id):
        # 接收参数
        json_str = request.body.decode()
        import json
        json_dict = json.loads(json_str)
        password = json_dict.get("password")
        password2 = json_dict.get("password2")
        access_token = json_dict.get("access_token")

        # 校验参数
        try:
            user = User.objects.get(id=user_id)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({"status": 5002, 'message': "没有该用户!"})

        # 校验密码是否一致
        # 正则校验
        if password != password2:
            return http.HttpResponseForbidden("密码不一致")

        user.set_password(raw_password=password)
        user.save()

        return http.JsonResponse({"status": 500, 'message': "成功修改密码!"})



# 微博登录---跳转到微博登录页
class SianLogin(View):
    """
    APP_KEY='3305669385'
    APP_SECRET='74c7bea69d5fc64f5c3b80c802325276'
    REDIRECT_URL='http://www.meiduo.site:8000/sina_callback'
    """
    def get(self,request):

        from utils import sinaweibopy3
        client = sinaweibopy3.APIClient(
            # app_key： app_key值
            app_key=settings.APP_KEY,
            # app_secret：app_secret 值
            app_secret=settings.APP_SECRET,
            # redirect_uri ： 回调地址
            redirect_uri=settings.REDIRECT_URL
        )

        # 生成跳转的授权地址
        login_url = client.get_authorize_url()

        return http.JsonResponse({ "code": 0, "errmsg": '成功', "login_url": login_url})



# 微博绑定页面显示
class SianCallback(View):
    def get(self,requests):
        # 接收参数
        code = requests.GET.get("code")

        # 微博连接
        from utils import sinaweibopy3
        client = sinaweibopy3.APIClient(
            # app_key： app_key值
            app_key=settings.APP_KEY,
            # app_secret：app_secret 值
            app_secret=settings.APP_SECRET,
            # redirect_uri ： 回调地址
            redirect_uri=settings.REDIRECT_URL
        )
        # 通过code获得token
        result = client.request_access_token(code)
        access_token = result.access_token
        uid = result.uid

        uid = int(uid)
        # print(type(uid))
        try:
            user_sian = OAuthSinaUser.objects.get(uid=uid)
        except Exception as e:
            logger.error(e)
            return render(requests, 'sina_callback.html', context={'uid': str(uid)})
        else:
            user = user_sian.user
            user = User.objects.get(id=user.id)
            login(requests, user)

            # response = http.JsonResponse({"status": 5000})
            response = redirect(reverse("users:index"))
            # response = http.HttpResponseRedirect(reverse('users:index'))
            # response = render(requests,"index.html",context={'uid': str(uid)})

            response.set_cookie("username", user.username, max_age=14 * 24 * 3600)
            # try:
            #     OAuthSinaUser.objects.create(uid=uid,user_id=user.id)
            # except Exception as e:
            #     logger.error(e)

            # login(request,user=user)

            # response = redirect(reverse("users:index"))
            # response = redirect(reverse("users:index"))
            # # 设置cookie
            # response.set_cookie("username", user.username, max_age=3600 * 24 * 15)

            return response


#  绑定用户提交

class OauthSinaUser(View):
    def post(self,request):
        # 接收参数
        json_dict = json.loads(request.body.decode())
        mobile = json_dict.get("mobile")
        password = json_dict.get("password")
        sms_code = json_dict.get("sms_code")
        uid = json_dict.get("uid")

        # 校验参数
        if not all([sms_code, password,mobile,uid]):
            return http.HttpResponseForbidden("参数不全")

        if not re.match(r"^[0-9A-Za-z]{8,20}", password):
            return render(request, 'sina_callback.html', {'account_errmsg': '用户名或密码错误'})

        if not re.match(r"^[0-9]{11}", mobile):
            return http.HttpResponseForbidden("手机号有误！请检查")

        # 链接ｒｅｄｉｓ
        client = get_redis_connection("sms_code")
        try:
            sms_redis_code = client.get("sms_%s" % mobile)
        except Exception as e:
            logger.error(e)
            return render(request, 'sina_callback.html', {'sms_code_errmsg': '无效的短信验证码'})

        if sms_redis_code.decode() != sms_code:
            return render(request, 'sina_callback.html', {'sms_code_errmsg': '输入短信验证码有误'})
        # try:
        #     sinauser = OAuthSinaUser.objects.get(uid=uid)
        # except Exception as e:
        #     logger.error(e)
        # user = User.objects.get(id=sinauser.user_id)

        # 判断微博是否绑定
        try:
           a = OAuthSinaUser.objects.get(uid=uid)
        except:
            # 如果不绑定
            # 判断手机号这个用户是否存在
            try:
                user = User.objects.get(mobile=mobile)
            except Exception as e:
                logger.error(e)
                # 如果该用户不存在
                try:
                    user = User.objects.create_user(username=mobile, password=password)
                    user.mobile = mobile
                    user.save()
                except Exception as e:
                    logger.error(e)
                    return http.HttpResponseForbidden("数据库问题")

                try:
                    OAuthSinaUser.objects.create(uid=uid, user_id=user.id)
                except Exception as e:
                    logger.error(e)

                return http.JsonResponse({"status": 5000})

            # 如果存在
            # 判断密码正不正确
            if not user.check_password(raw_password=password):
                return render(request, 'sina_callback.html', {'account_errmsg': '密码错误'})
            # 如果密码正确
            try:
                OAuthSinaUser.objects.create(uid=uid, user_id=user.id)
            except Exception as e:
                logger.error(e)

            login(request,user=user)
            response = http.JsonResponse({"status": 5000})

            response.set_cookie("username",user.username,max_age=14*24*3600)

            return response

        # 如果绑定了
        user = User.objects.get(id=a.user_id)
        login(request,user)
        response = http.JsonResponse({"status": 5000})
        response.set_cookie("username",user.username,max_age=14*24*3600)
        return response




# 我的订单

class OrderInfo(LoginRequiredMixin,View):
    def get(self,reques,page_num):
        # 接收参数
        # 校验参数
        # 查询数据库获得订单
        """
         # 每页显示的内容
            "page_orders": page_orders,
            # 总页数
            'total_page': total_page,
            # 当前页
            'page_num': page_num,
        """
        # 将以上参数查询
        contex = {
            # 每页显示的内容
        }

        #  拼接参数，返回给前端







