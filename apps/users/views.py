import json
import re

from django.conf import settings
from django.core.mail import send_mail
from django import http
from django.contrib.auth.views import login, logout

from apps.areas.models import Area
from apps.goods.models import GoodsChannel, SKU
from utils.secret import SecretOauth
from django.shortcuts import render, redirect
from random import randint
# Create your views here.
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection
from pymysql import DatabaseError
from apps.users import constants
from apps.users.models import User, ContentCategory
from libs.captcha.captcha import captcha
from meiduo_mall.settings.dev import logger
from utils.response_code import RETCODE

# 注册函数
class Register(View):
    def get(self,request):
        return render(request,"register.html")


    def post(self,request):
        # 接收变量
        username = request.POST.get("username")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        mobile = request.POST.get("mobile")
        # image_code = request.POST.get("image_code")
        sms_code = request.POST.get("msg_code")
        allow = request.POST.get("allow")

        #　效验参数
        if  all([username, password, password2, mobile, allow]):
            if not re.match(r"^[a-zA-Z0-9]{5,20}$",username):
                return http.HttpResponseForbidden('请输入5-20个字符的用户名')
            if not re.match(r"^[0-9A-Za-z]{8,20}",password):
                return http.HttpResponseForbidden("请输入8-20个字符的密码")
            if password2 != password:
                return http.HttpResponseForbidden("，密码不一致请确认密码")
            if not re.match(r"^[0-9]{11}",mobile):
                return http.HttpResponseForbidden("手机号有误！请检查")
            if allow != "on":
                return http.HttpResponseForbidden("没有勾选同意用户协议！")
            redis_client = get_redis_connection("sms_code")
            try:
                b = redis_client.get("sms_%s" % mobile)
            except BaseException:
                return render(request, 'register.html', {'sms_code_errmsg': '无效的短信验证码'})
            try:
                if b.decode() != sms_code:
                    return render(request, 'register.html', {'sms_code_errmsg': '输入短信验证码有误'})
            except Exception as e:
                logger.error(e)

        else:
            return http.HttpResponseForbidden("缺少必要参数")

        # # 判断参数是否齐全
        # if not all([username, password, password2, mobile, allow]):
        #     return http.HttpResponseForbidden('缺少必传参数')
        # # 判断用户名是否是5-20个字符
        # if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
        #     return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        # # 判断密码是否是8-20个数字
        # if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
        #     return http.HttpResponseForbidden('请输入8-20位的密码')
        # # 判断两次密码是否一致
        # if password != password2:
        #     return http.HttpResponseForbidden('两次输入的密码不一致')
        # # 判断手机号是否合法
        # if not re.match(r'^1[3-9]\d{9}$', mobile):
        #     return http.HttpResponseForbidden('请输入正确的手机号码')
        # # 判断是否勾选用户协议
        # if allow != 'on':
        #     return http.HttpResponseForbidden('请勾选用户协议')

        # 保存注册数据
        try:
           user =  User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg': '注册失败'})

        login(request, user)

        # 响应注册结果
        return redirect(reverse("users:index"))


# 转到首页
class Index(View):
    def get(self,request):
        # 商品分类页
        from apps.goods.utils import get_categories
        categories = get_categories()

        # 查询所有广告类别
        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        # 轮播图


        # 快讯

        # 页头广告

        # 渲染模板的上下文
        context = {
            "categories":categories,
            "contents":contents,
        }

        return render(request,"index.html",context)


# 判断用户名是否重复
class Userconut(View):
    def get(self,request,username):
        # 接收参数
        # 校验
        # 数据库查询
        count = User.objects.filter(username=username).count()
        # 返回响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})

# 判断手机号是否重复
class Mobilecount(View):
    def get(self,request,mobile):
        # 接收参数
        # 校验
        # 数据库查询
        count = User.objects.filter(mobile=mobile).count()

        #　返回响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})

# 生成图形验证码并保存
class Captcha(View):
    def get(self,request,uuid):

        # 生成图片验证码
        text,image = captcha.generate_captcha()

        #
        # 保存图片验证码
        # 连接ｒｅｄｉｓ数据库
        redis_client = get_redis_connection('verify_image_code')
        # redis_client.setex('img_%s' % uuid,constants.IMAGE_CODE_REDIS_EXPIRES, text)
        # 写入数据
        redis_client.setex('img_%s' % uuid, 300 , text)


        return http.HttpResponse(image,content_type="image/jpg")


# 手机验证码验证，同时验证图形码
class Sms_codes(View):
    def get(self,request,mobile):
        image_code = request.GET.get("image_code")
        uuid = request.GET.get("image_code_id")

        redis_client = get_redis_connection("verify_image_code")
        try:
            a = redis_client.get('img_%s' % uuid)
        except BaseException:
            return http.JsonResponse({'code': "4001", 'errmsg': '图形码过期'})
        try:
            redis_client.delete('img_%s' % uuid)
        except Exception as e:
            logger.error(e)
        try:
            if a.decode().lower() != image_code.lower():
                return http.JsonResponse({'code': "4001", 'errmsg': '输入图形验证码有误'})
        except Exception as e:
            logger.error(e)

        # 设计６位随机的短信验证码
        sms_code = randint(100000,999999)
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

        return http.JsonResponse({'code': '0', 'errmsg': '发送短信成功'})


# 登陆页面和登陆实现
class Login(View):
    def get(self,request):
        return render(request,"login.html")


    def post(self,request):
        # 接收参数
        username = request.POST.get("username")
        password = request.POST.get("password")
        remembered = request.POST.get("remembered")

        # 校验


        #　数据库查询

        try:
            from django.contrib.auth import authenticate
            user = authenticate(username= username,password=password)
        except User.DoesNotExist as e:
            logger.error(e)


        # 判断是否记住登陆
        if remembered == "on":
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)


        # 判断用户是否存在
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})
        else:
            # 设置ｓｅｓｓｉｏｎ
            login(request, user)
            next = request.GET.get("next")
            if next:
                response = redirect(next)
                response.set_cookie("username",user.username,max_age=3600*24*15)
                return response
            else:
                response = redirect(reverse("users:index"))
                # 设置cookie
                response.set_cookie("username",user.username,max_age=3600*24*15)

                # 合并购物车
                from apps.carts.utils import merge_cart_cookie_to_redis
                merge_cart_cookie_to_redis(request, response)

                return response



# 退出登录页的实现
class Logout(View):

    def get(self,request):
        # 删除ｓｅｓｓｉｏｎ
        logout(request)
        # 重定向到首页
        response = redirect(reverse("users:index"))
        response.delete_cookie("username")
        return response


# 用户中心，判断是否登陆
from django.contrib.auth.mixins import LoginRequiredMixin
class Info(LoginRequiredMixin,View):

    def get(self,request):
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active
        }
        return render(request,"user_center_info.html",context)



#　用户中心添加邮箱
class Emails(LoginRequiredMixin,View):
    def put(self,request):
        json_str = request.body.decode()
        # print(json_str)
        import json
        json_dict = json.loads(json_str)
        email = json_dict.get('email')
        # print(request.user)
        # print(email)
        # username= json_dict.get("username")
        # print(username)
        # request.user.email= email
        # request.user.save()
        # 校验
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('参数email有误')

        # 1.加密的数据
        data_dict = {'user_id': request.user.id, "email": request.user.email}
        # 2. 进行加密数据

        secret_data = SecretOauth().dumps(data_dict)

        # 发送邮件
        #subject 邮件标题
        # message 普通邮件正文，普通字符串
        # from_email 发件人
        # recipient_list 收件人列表
        # html_message 多媒体邮件正文，可以是html字符串


        subject = "美多商城邮箱验证"
        # subject = "ai爱直播"
        verify_url = settings.EMAIL_VERIFY_URL + '?token=' + secret_data

        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用美多商城。</p>' \
                       '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                       '<p><a href="%s">%s</a></p>' % (email,verify_url, verify_url)
        # html_message = '<p>尊敬的用户赵博您好！</p>' \
        #                '<p>感谢您的注册</p>' \
        #                '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
        #                '<p><a href="http://www.sharesome.com">点此进入</a></p>' % (email)

        send_mail(subject, message="1", from_email="hmmeiduo@163.com", recipient_list=[email], html_message=html_message)

        # 保存数据库中
        try:
            User.objects.filter(username=request.user).update(email=email)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '添加邮箱失败'})

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})


# 验证邮箱
class Emailsverification(LoginRequiredMixin,View):
    def get(self,request):
        token = request.GET.get("token")
        print(token)
        # 校验参数：判断token是否为空和过期，提取user
        if not token:
            return http.HttpResponseBadRequest('缺少token')

        # 解密
        # token_dict = SecretOauth().loads(token)
        # print(a,type(a))
        try:
            request.user.email_active = True
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('激活邮件失败')

        return redirect(reverse('users:info'))



# 修改密码－－－－－用户页的
class ChangePassword(View):
    # 转到密码修改页
    def get(self,request):
        return render(request,"user_center_pass.html")

    # 修改密码逻辑实现
    def post(self,request):
        #　接受参数
        old_pwd = request.POST.get("old_pwd")
        new_pwd = request.POST.get("new_pwd")
        new_cpwd = request.POST.get("new_cpwd")
        # 校验
        # 1.正则校验
        if not re.match(r"^[0-9A-Za-z]{8,20}", old_pwd):
            return render(request,"user_center_pass.html", {'origin_pwd_errmsg':'原始密码错误'})
        else:
            try:
                result = request.user.check_password(old_pwd)
            except Exception as e:
                logger.error(e)
                return render(request, 'user_center_pass.html', {'origin_pwd_errmsg': '原始密码错误'})
            if not result:
                return render(request, 'user_center_pass.html', {'origin_pwd_errmsg':'原始密码错误'})
            if not re.match(r"^[0-9a-zA-Z]{8,20}", new_pwd):
                return http.HttpResponse("请输入８－２０个字符的密码")
            else:
                if new_cpwd != new_pwd:
                    return http.HttpResponse("俩次密码不一致")



        # 逻辑实现
        try:
            request.user.set_password(new_pwd)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return render(request, 'user_center_pass.html', {'origin_pwd_errmsg':'更新失败'})

        login(request)
        response = redirect(reverse("users:login"))
        response.delete_cookie("username")

        # 返回
        return response



# 保存和查询浏览记录
class BrowseHistories(LoginRequiredMixin,View):
    def post(self,request):
        # 接收参数
        sku_id = json.loads(request.body.decode()).get("sku_id")

        # 校验
        #　1.校验商品是否存在
        try:
            sku = SKU.objects.get(id=sku_id)
        except:
            return http.HttpResponseForbidden("商品不存在")

        # 如果有ｓｋｕ就保存都ｒｅｄｉｓ中
        # 链接ｒｅｄｉｓ
        client = get_redis_connection("history")
        history_key = request.user.id
        # 不懂
        redis_pipeline = client.pipeline()
        # 去重
        client.lrem(history_key,0,sku_id)

        # 存储
        client.lpush(history_key,sku_id)

        #　截取５个
        client.ltrim(history_key,0,4)
        redis_pipeline.execute()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})


    def get(self,request):
        # 显示用户浏览记录
        # 链接ｒｅｄｉｓ
        client = get_redis_connection("history")
        sku_ids = client.lrange(request.user.id,0,-1)
        skus = []
        # sku_ids 是该用户浏览的商品信息
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            skus.append({
                "id":sku.id,
                "name":sku.name,
                "default_image_url":sku.default_image.url,
                "price":sku.price
            })

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'skus': skus})





























