import json

from django_redis import get_redis_connection

from utils.cookiesecret import CookieSecret


def merge_cart_cookie_to_redis(request,response):
    """
        登录后合并cookie购物车数据到Redis
        :param request: 本次请求对象，获取cookie中的数据
        :param response: 本次响应对象，清除cookie中的数据
        :return: response
    """
    # 查询ｃｏｏｋｉｅ将ｃｏｏｋｉｅ中的数据都提取出来
    cookie_str = request.COOKIES.get("carts")

    # 判断ｃｏｏｋｉｅ里是否有数据
    if cookie_str:
        # 连接ｒｅｄｉｓ数据库
        client = get_redis_connection("carts")

        # 将取出来的ｃｏｏｋｉｅ数据解密
        cookie_dict = CookieSecret.loads(cookie_str)

        # 覆盖ｒｅｄｉｓ里的数据
        for sku_id in cookie_dict.keys():
            client.hset(request.user.id,sku_id,json.dumps(cookie_dict[sku_id]))

        # 删除ｃｏｏｋｉｅ
        response.delete_cookie("carts")

