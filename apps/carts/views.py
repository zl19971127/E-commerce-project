import json

from django import http
from django.shortcuts import render

# 购物车增加
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU
from utils.cookiesecret import CookieSecret
from utils.response_code import RETCODE

# 添加商品到购物车
class CartsView(View):
    # 增
    def post(self,request):
        # 接收参数
        sku_id = json.loads(request.body.decode()).get("sku_id")
        count = json.loads(request.body.decode()).get("count")
        selected = json.loads(request.body.decode()).get("selected", True)

        # 校验
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断sku_id是否存在
        try:
            sku = SKU.objects.get(id=sku_id)
        except Exception as e:
            return http.HttpResponseForbidden('商品不存在')

        # 判断count是否是数字
        try:
            count = int(count)
        except:
            return http.HttpResponseForbidden('参数count有误')

        # 判断selected是否为bool值
        if selected:
            if not isinstance(selected,bool):
                return http.HttpResponseForbidden('参数selected有误')

        #  判断用户是否登录
        if request.user.is_authenticated():
            # 以登录就用ｒｅｄｉｓ存储
            # 链接redis数据库
            cenlit = get_redis_connection('carts')
            # 获取以前数据库的值
            cenlit_data = cenlit.hgetall(request.user.id)

            if str(sku_id).encode() in cenlit_data:
                # 根据sku_id 取出商品
                child_dict = json.loads(cenlit_data[str(sku_id).encode()].decode())
                # 个数累加
                child_dict["count"] += count
                # 更新数据
                cenlit.hset(request.user.id, sku_id, json.dumps(child_dict))
            else:
                # 如果商品已经不存在--直接增加商品数据
                cenlit.hset(request.user.id, sku_id, json.dumps({'count': count, 'selected': selected}))

            return  http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})

        else:
            # 未登录就用cooike存储
            carts_str = request.COOKIES.get("carts")

            # 如果用户操作过cookie购物车
            if carts_str:
                # 解密出明文
                carts_dict = CookieSecret.loads(carts_str)
            else:
                carts_dict = {}

            # 判断要加入购物车的商品是否已经在购物车中,如有相同商品，累加求和，反之，直接赋值
            if sku_id in carts_dict:
                # 累加求和
                origin_count = carts_dict[sku_id]["count"]
                count += origin_count

            carts_dict[sku_id] = {
                "count":count,
                "selected":selected,
            }
            carts_dict_str = CookieSecret.dumps(carts_dict)

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})
            # 响应结果并将购物车数据写入到cookie
            response.set_cookie('carts', carts_dict_str, max_age=24 * 30 * 3600)

            return response

    # 查
    def get(self,request):
        user = request.user
        if user.is_authenticated:
            client = get_redis_connection("carts")
            carts_data = client.hgetall(user.id)
            carts_dict = {}
            for key,value in carts_data.items():
                sku_id = int(key.decode())
                sku_dict = json.loads(value.decode())
                carts_dict[sku_id]= sku_dict
        else:
            cookie_str = request.COOKIES.get("carts")
            if cookie_str:
                carts_dict = CookieSecret.loads(cookie_str)

        sku_ids = carts_dict.keys()

        skus = SKU.objects.filter(id__in=sku_ids)
        carts_skus = []
        for sku in skus:
            carts_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': carts_dict.get(sku.id).get('count'),
                'selected': str(carts_dict.get(sku.id).get('selected')),  # 将True，转'True'，方便json解析
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),  # 从Decimal('10.2')中取出'10.2'，方便json解析
                'amount': str(sku.price * carts_dict.get(sku.id).get('count')),
            })
            context = ({
                'cart_skus': carts_skus,
            })

        return render(request,"cart.html", context)

    #　改
    def put(self,request):
        # 接收参数
        sku_id = json.loads(request.body.decode()).get("sku_id")
        count = json.loads(request.body.decode()).get("count")
        selected = json.loads(request.body.decode()).get("selected")

        # 校验
        try:
            sku = SKU.objects.get(id=sku_id)
        except Exception as e:
            return http.HttpResponseForbidden("没有这个商品")

        # 判断是否登陆
        user = request.user
        if user.is_authenticated:
            # 修改redis
            redis_client = get_redis_connection("carts")
            # 覆盖ｒｅｄｉｓ以前所有数据
            new_data = {"count":count,"selected":selected}
            redis_client.hset(user.id,sku_id,json.dumps(new_data))
        else:
            # 修改ｃｏｏｋｉｅ
            # 指定ｃｏｏｋｉｅ
            cart_str = request.COOKIES.get("carts")
            if cart_str:
                # 将ｃｏｏｋｉｅ中的数据解密
                cart_dict = CookieSecret.loads(cart_str)
            else:
                cart_dict = {}
            # 将原来的数据覆盖
            cart_dict[sku_id]={
                "count":count,
                "selected":selected
            }
            # 将明文转化为密文
            cookie_dict_str = CookieSecret.dumps(cart_dict)

        cart_sku={
            "id":sku.id,
            "count":count,
            "selected":selected,
            "name":sku.name,
            "default_image_url":sku.default_image.url,
            "price":sku.price,
            "amount":sku.price * count,
        }

        response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})

        # 如果用户没有登录就创建一个新cookie
        if not user.is_authenticated:
            response.set_cookie("carts",cookie_dict_str, max_age=24 * 14 * 3600)

        return response


    # 删
    def delete(self,request):
        # 接收参数
        sku_id = json.loads(request.body.decode()).get("sku_id")
        # 校验
        try:
           SKU.objects.get(id=sku_id)
        except:
            return http.HttpResponseForbidden("商品不存在")
        user = request.user
        # 判断是否登陆
        if user.is_authenticated:
            # 删除redis里的数据
            # 链接redis数据库
            client = get_redis_connection("carts")
            # 查询数据库所有数据
            # 删除数据库该商品
            client.hdel(user.id,sku_id)
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除购物车成功'})

        else:
            # 删除cookie里的数据
            # 获得指定的cookie
            carts_str = request.COOKIES.get("carts")
            # 解密 获得字典
            try:
                carts_dict = CookieSecret.loads(carts_str)
            except:
                carts_dict = {}

            #　删掉对应的商品
            if sku_id in carts_dict.keys():
                del carts_dict[sku_id]
                # 将字典转成密文
                cookie_cart_str = CookieSecret.dumps(carts_dict)
                response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '删除购物车成功'})
                response.set_cookie("carts",cookie_cart_str,max_age=14*24*3600)
            return response

# 首页购物车显示
class CartSimpleView(View):
    def get(self,request):
        user = request.user
        if user.is_authenticated:
            # 链接ｒｅｄｉｓ数据库
            client = get_redis_connection("carts")
            # 取出所有商品数据
            carts_data = client.hgetall(user.id)
            # 转换格式
            cart_dict = {int(key.decode()): json.loads(value.decode()) for key, value in carts_data.items()}

        else:
            carts_str = request.COOKIES.get("carts")
            if carts_str:
                cart_dict = CookieSecret.loads(carts_str)
            else:
                cart_dict = {}

        cart_skus = []
        sku_ids = cart_dict.keys()
        skus = SKU.objects.filter(id__in = sku_ids)
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': cart_dict.get(sku.id).get('count'),
                'default_image_url': sku.default_image.url
            })
        return http.JsonResponse({'code':RETCODE.OK, 'errmsg':'OK', 'cart_skus':cart_skus})


# 全选购物车
class CartSelectionView(View):
    def put(self,request):
        #　接收参数
        selected = json.loads(request.body.decode()).get("selected")
        # 判断是否登陆
        user = request.user
        if user.is_authenticated:
            # 查询ｒｅｄｉｓ数据库
            client = get_redis_connection("carts")
            carts_data = client.hgetall(user.id)
            for key,value in carts_data.items():
                sku_id = int(key.decode())
                carts_dict = json.loads(value.decode())
                carts_dict["selected"] = selected
                client.hset(user.id,sku_id,json.dumps(carts_dict))
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '全选购物车成功'})

        else:
            # 找到指定ｃｏｏｋｉｅ
            carts_str = request.COOKIES.get("carts")
            # 判断ｃａｒｔｓ_str　有没有
            if carts_str:
                carts_dict = CookieSecret.loads(carts_str)
                for sku_id in carts_dict.keys():
                    carts_dict[sku_id]["selected"] = selected
                cookie_cart = CookieSecret.dumps(carts_dict)
                response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '全选购物车成功'})
                response.set_cookie('carts', cookie_cart, 24 * 30 * 3600)

            return response




