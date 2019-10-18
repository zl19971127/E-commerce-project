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
from rest_framework_jwt.views import obtain_jwt_token

from apps.meiduo_admin.views import admin
from apps.meiduo_admin.views import options
from apps.meiduo_admin.views import AtatisticalAndUser
from apps.meiduo_admin.views import brands
from apps.meiduo_admin.views import goods
from apps.meiduo_admin.views import images
from apps.meiduo_admin.views import sku
from apps.meiduo_admin.views import order
from apps.meiduo_admin.views import perms
from apps.meiduo_admin.views import group
from apps.meiduo_admin.views import categories
from rest_framework.routers import SimpleRouter

urlpatterns = [
    # 管理员登录
    url(r'^authorizations/$', obtain_jwt_token),

    # 用户总量统计
    url(r'^statistical/total_count/$',AtatisticalAndUser.UserTotalCountView.as_view(),name="total_count"),

    # 日增用户统计
    url(r'^statistical/day_increment/$',AtatisticalAndUser.UserDayCountView.as_view(),name="day_increment"),

    # 日活跃用户
    url(r'^statistical/day_active/$',AtatisticalAndUser.UserActiveCountView.as_view(),name="day_active"),

    # 日下单用户量统计
    url(r'^statistical/day_orders/$',AtatisticalAndUser.UserOrderCountView.as_view(),name="day_orders"),

    # 月增用户统计
    url(r'^statistical/month_increment/$',AtatisticalAndUser.UserMonthCountView.as_view(),name="month_increment"),

    # 日分类商品访问量
    url(r'^statistical/goods_day_views/$',AtatisticalAndUser.GoodsDayView.as_view(),name="goods_day_views"),

    # 用户查询
    url(r'^users/$',AtatisticalAndUser.UserView.as_view(),name="users"),

    # 查询规格
    url(r'^goods/simple/$', goods.SPUSimpleView.as_view(),name="simple"),

    # ＳＰＵ创建中的品牌查询
    url(r'^goods/brands/simple/$', goods.SPUBrandviews.as_view(),name="brands"),

    # SPU中查询一级分类
    url(r'^goods/channel/categories/$', goods.SPUCategoriesViews.as_view(),name="categories1"),

    # SPU中查询二级分类
    url(r'^goods/channel/categories/(?P<pk>\d+)/$', goods.SPUCategories2Views.as_view(), name="categories2"),

    # SKU中查询三级所有分类
    url(r'^skus/categories/$', sku.GoodsCategory3Views.as_view(), name="categories"),

    # SKU中根据spu_id查询规格
    url(r"^goods/(?P<pk>\d+)/specs/$",sku.Specsviews.as_view(),name="specs1"),

    # SPU中上传图片
    url(r"^goods/images/$", goods.ImagesViews.as_view(), name="images"),

    # # 品牌的查询和创建
    # url(r"^goods/brands/$", brands.BrandsViews.as_view(), name="brands"),
    # # 品牌查询一个和修改，删除
    # url(r"^goods/brands/(?P<pk>\d+)/$", brands.BrandView.as_view(), name="brand"),

    # 商品规格选项中查询品牌信息
    url(r"^goods/specs/simple/$", options.SimpleView.as_view(), name="simple1"),


    # 图片查询中skuid的查询
    url(r"^skus/simple/$", sku.SKUSimpleView.as_view(), name="simple2"),

    # 权限的简单查询
    url(r"^permission/content_types/$",perms.PermsSimpleView.as_view(),name="PermsSimple"),

    # 用户组简单查询
    url(r"^permission/groups/simple/$",group.GroupSmipleView.as_view(),name="groupSmiple"),

    # 权限简单查询
    url(r"^permission/simple/$",perms.PermsSimpleView.as_view(),name="PermsSimple1"),

    # 商品类别查询
    url(r"^goods/categories/$", categories.CategoriesView.as_view(),name="categories"),

]

router = SimpleRouter()
# 品牌
router.register("goods/brands",brands.BrandsViews,base_name="brands")
# 商品规格查询，修改，创建，删除
router.register("goods/specs",goods.GoodsViews,base_name="specs")
# SPU
router.register("goods",goods.SPUViews,base_name="goods")
# 图片查询
router.register('skus/images', images.ImageViewSet, base_name='images')
# SKU
router.register("skus",sku.SKUViewSet,base_name="skus")
# # 规格选项
router.register("specs/options",options.OptionsViewset,base_name="options")
# 订单
router.register("orders",order.OrdersViewSet,base_name="orders")
# 权限
router.register("permission/perms",perms.PermsViewSet,base_name="perms")
# 用户组管理
router.register("permission/groups",group.GroupViewSet,base_name="groups")
# 管理员管理
router.register("permission/admins",admin.AdminViewSet,base_name="admins")
urlpatterns += router.urls
