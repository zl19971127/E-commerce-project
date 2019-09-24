import json
from datetime import datetime

from decimal import Decimal

from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU
from apps.orders.models import OrderInfo, OrderGoods
from apps.users.models import Address
from utils.response_code import RETCODE


class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""

    def get(self, request):
        """提供订单结算页面"""
        # 获取登录用户
        user = request.user

        # 1.查询地址
        try:
            addresses = Address.objects.filter(user=user, is_deleted=False)

        except:
            #  如果地址为空，渲染模板时会判断，并跳转到地址编辑页面
            addresses = None

        # 2.查询选中商品
        redis_client = get_redis_connection('carts')
        carts_data = redis_client.hgetall(user.id)
        # 转换格式
        carts_dict = {}
        for key,value in carts_data.items():
            sku_id = int(key.decode())
            sku_dict = json.loads(value.decode())
            if sku_dict['selected']:
                carts_dict[sku_id] = sku_dict

        # 3.计算金额 +邮费
        total_count = 0
        total_amount = Decimal(0.00)

        skus = SKU.objects.filter(id__in=carts_dict.keys())

        for sku in skus:
            sku.count = carts_dict[sku.id].get('count')
            sku.amount = sku.count * sku.price
            # 计算总数量和总金额
            total_count += sku.count
            total_amount += sku.count * sku.price

        # 运费
        freight = Decimal('10.00')

        # 4.构建前端显示的数据
        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight,
             'default_address_id':user.default_address_id
        }
        return render(request, 'place_order.html', context)



class OrderCommitView(View):

    def post(self,request):
        """保存订单信息和订单商品信息"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get("address_id")
        pay_method = json_dict.get("pay_method")

         # 校验参数
        if not all([address_id, pay_method]):
            return http.HttpResponseForbidden('缺少必传参数')
            # 判断address_id是否合法
        try:
            address = Address.objects.get(id=address_id)
        except Exception:
            return http.HttpResponseForbidden('参数address_id错误')
            # 判断pay_method是否合法
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('参数pay_method错误')

        # 获取登陆的用户
        user = request.user
        # 生成订单编号
        order_id = datetime.now().strftime("%Y%m%d%H%M%S")+("%9d" % user.id)
        # 保存订单的基本信息
        order = OrderInfo.objects.create(
            order_id=order_id,
            user=user,
            address=address,
            total_count=0,
            total_amount=Decimal('0'),
            freight=Decimal('10.00'),
            pay_method=pay_method,
            status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'] else
            OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        )


        # 从购物车里　取出选中的商品
        redis_client = get_redis_connection("carts")
        carts_data = redis_client.hgetall(user.id)
        carts_dict = {}
        for key,value in carts_data.items():
            sku_id = int(key.decode())
            sku_dict = json.loads(value.decode())
            if sku_dict["selected"] is True:
                carts_dict[sku_id] = sku_dict

        # 遍历选中的商品信息
        sku_ids = carts_dict.keys()
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            # 判断库存是否充足
            cart_count = carts_dict[sku_id].get("count")
            if cart_count >sku.stock:
                return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})

            # sku减少库存，增加销量
            sku.stock -= cart_count
            sku.sales += cart_count
            sku.save()

            # ｓｐｕ增加销量
            sku.spu.sales += cart_count
            sku.spu.save()

            # 保存订单商品信息
            OrderGoods.objects.create(
                order=order,
                sku=sku,
                count=cart_count,
                price=sku.price,
            )

            # 保存商品订单中总价和总数量
            order.total_count += cart_count
            order.total_amount += (cart_count * sku.price)
            order.save()

        # 添加邮费和保存订单
        order.total_amount += order.freight
        order.save()

        # 清除购物车已经结算过得商品
        redis_client.hdel(user.id,*carts_dict)
        # 返回响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '下单成功', 'order_id': order.order_id})


class OrderSuccessView(View):
    def get(self,request):
        return render(request,"order_success.html")
