from apps.goods.models import GoodsChannel


def get_categories():
    # 提供动态的首页广告
    # 查询商品频道和分类
    categories = {}  # 存频道组
    channels = GoodsChannel.objects.all().order_by("sequence")
    for channel in channels:
        # 　取商品频道组
        group_id = channel.group
        if group_id not in categories:
            categories[group_id] = {
                "channels": [],
                "sub_cats": []
            }
        # 取一级分类
        cat1 = channel.category
        categories[group_id]["channels"].append({
            "id": cat1.id,
            "name": cat1.name,
            "url": channel.url,
        })
        # print(cat1.subs)
        # 构建当前类别的子类别
        cat2 = cat1.subs.all()
        for a in cat2:
            a.sub_cats = []
            cat3 = a.subs.all()
            for b in cat3:
                a.sub_cats.append(b)
            categories[group_id]['sub_cats'].append(a)

    return categories

def get_breadcrumb(cat3):
    """
    获取面包屑导航
    :param category: 商品类别三级
    :return: 面包屑导航字典
    """
    # 根据三级取二级
    cat2 = cat3.parent

    # 根据耳机取一级
    cat1 = cat2.parent
    # 前端需要的数据
    breadcrumb = {
        'cat1': {
            # 根据一级分类关联频道获取频道的url
            "url": cat1.goodschannel_set.all()[0].url,
            'name': cat1.name
        },
        "cat2": cat2,
        "cat3": cat3,
    }
    return breadcrumb