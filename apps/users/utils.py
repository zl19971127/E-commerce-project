# from django.contrib.auth.backends import ModelBackend
# import re
# from .models import User
#
#
# def get_user_by_account(account):
#     """
#     根据account查询用户
#     :param account: 用户名或者手机号
#     :return: user
#     """
#     try:
#         if re.match('^1[3-9]\d{9}$', account):
#             # 手机号登录
#             user = User.objects.get(mobile=account)
#         else:
#             # 用户名登录
#             user = User.objects.get(username=account)
#     except User.DoesNotExist:
#         return None
#     else:
#         return user
#
#
# class UsernameMobileAuthBackend(ModelBackend):
#     """自定义用户认证后端"""
#
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         """
#         重写认证方法，实现多账号登录
#         :param request: 请求对象
#         :param username: 用户名
#         :param password: 密码
#         :param kwargs: 其他参数
#         :return: user
#         """
#         # 根据传入的username获取user对象。username可以是手机号也可以是账号
#         user = get_user_by_account(username)
#         # 校验user是否存在并校验密码是否正确
#         if user and user.check_password(password):
#             return user
import re

from django.contrib.auth.backends import ModelBackend

from apps.users.models import User
from meiduo_mall.settings.dev import logger


class UsernameMobileAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 判断是前台的访问还是后台的访问
        if request == None:
            # 后台的访问
            try:
                if re.match(r"^[0-9]{11}",username):
                    user = User.objects.get(mobile=username)
                else:
                    user = User.objects.get(username= username,is_staff=True)
            except Exception as e:
                logger.error(e)
                return None
            else:
                if user.check_password(password):
                    return user
                else:
                    user = None
                    return user
        else:
            # 前台的访问

            try:
                if re.match(r"^[0-9]{11}",username):
                    user = User.objects.get(mobile=username)
                else:
                    user = User.objects.get(username= username)
            except Exception as e:
                logger.error(e)
            else:
                if user.check_password(password):
                    return user
                else:
                    user = None
                    return user

