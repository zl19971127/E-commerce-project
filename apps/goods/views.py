from django import http
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View

from apps.goods import models
from apps.goods.utils import get_categories, get_breadcrumb
from utils.response_code import RETCODE


class ListView(View):
    def get(self,request,category_id,page_num):
        try:
            category = models.GoodsCategory.objects.get(id=category_id)
        except models.GoodCategory.DoesNotExist:
            return http.HttpResponseNotFound('GoodsCategory does not exist')

        # 接收sort参数：如果用户不传，就是默认的排序规则
        sort = request.GET.get("sort","default")

        # 查询商品频道分类
        categories = get_categories()

        # 查询面包屑导航
        breadcrumb = get_breadcrumb(category)

        # 按照排序规则查询该分类商品SKU信息
        if sort == "price":
            # 按照价格由低到高
            sort_field = "price"
        elif sort == "hot":
            # 按照销量由高到低
            sort_field = "-sales"
        else:
            # 'price'和'sales'以外的所有排序方式都归为'default'
            sort_field = 'create_time'
        skus = models.SKU.objects.filter(category=category, is_launched=True).order_by(sort_field)

        paginator = Paginator(skus,5)

        page_skus = paginator.page(page_num)

        total_page = paginator.num_pages

        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sort': sort,  # 排序字段
            'category': category,  # 第三级分类
            'page_skus': page_skus,  # 分页后数据
            'total_page': total_page,  # 总页数
            'page_num': page_num,  # 当前页码
        }
        return render(request,"list.html",context)



class HotGoodsView(View):
    """商品热销排行"""

    def get(self,request,category_id):
        # 根据销量倒序
        skus = models.SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:2]

        # 序列化
        hot_skus = []
        for sku in skus:
            hot_skus.append({
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price
            })

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK','hot_skus':hot_skus})



class DetailView(View):
    def get(self,request,sku_id):
        try:
            sku = models.SKU.objects.get(id=sku_id)
        except models.SKU.DoesNotExist:
            return render(request, '404.html')

            # 查询商品频道分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)

        # 渲染页面
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
        }
        return render(request, "detail.html",context)