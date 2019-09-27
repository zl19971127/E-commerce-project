import os

from django.conf import settings
from django.template import loader

from apps.goods.utils import get_categories
from apps.users.models import ContentCategory


def generate_static_index_html():
    """
    生成静态的主页ｈｔｍｌ文件
    :return:
    """
    categories = get_categories()

    # 广告内容
    contents = {}
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

    # 渲染模板
    context = {
        'categories': categories,
        'contents': contents
    }

    # 获取模板文件
    template = loader.get_template("index.html")
    # 渲染首页的html字符串
    html_text = template.render(context)
    # 将首页html字符串写入指定的目录，叫“index.html”
    file_path = os.path.join(settings.STATICFILES_DIRS[0],"index.html")

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html_text)