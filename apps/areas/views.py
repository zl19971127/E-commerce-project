import json
import re

from django import http
from django.shortcuts import render
from django.views import View

from apps.areas.models import Area
from apps.users.models import Address
from meiduo_mall.settings.dev import logger
from utils.response_code import RETCODE


class Addresses(View):
    def get(self,request):
        addresses = Address.objects.filter(user=request.user,is_deleted=False)
        address_dict_list = []
        for address in addresses:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_dict_list.append(address_dict)

        context = {
            'default_address_id': request.user.default_address_id,
            'addresses': address_dict_list,
        }
        return render(request,"user_center_site.html",context)


# 新增地址
class AddressCreate(View):
    def post(self, request):
        # 接受参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')

        # 校验参数
        # if not all([receiver, province_id, city_id, district_id, place, mobile]):
        #     return http.HttpResponseForbidden('缺少必传参数')
        # if not re.match(r'^1[3-9]\d{9}$', mobile):
        #     return http.HttpResponseForbidden('参数mobile有误')
        # if tel:
        #     if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
        #         return http.HttpResponseForbidden('参数tel有误')
        # if email:
        #     if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        #         return http.HttpResponseForbidden('参数email有误')

        # 保存地址
        try:
            address = Address.object.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email,
            )
            # address = Address.objects.create(
            #     user=request.user,
            #     title=receiver,
            #     receiver=receiver,
            #     province_id=province_id,
            #     city_id=city_id,
            #     district_id=district_id,
            #     place=place,
            #     mobile=mobile,
            #     tel=tel,
            #     email=email
            # )
            # address.save()
            # print(address)

            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            # print(e)
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})


# 三季联动
class AreasView(View):
    def get(self,request):
        area_id= request.GET.get("area_id")

        if not area_id:
            # 表示需要的是省的数据
            province_model_list = Area.objects.filter(parent__isnull=True)
            province_list = []
            for province_model in province_model_list:
             province_list.append({
                 "id":province_model.id,
                 "name":province_model.name
             })
            # # 序列化省级数据
            # province_list = []
            # for province_model in province_model_list:
            #     province_list.append({'id': province_model.id, 'name': province_model.name})

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})

        else:
            parent_model = Area.objects.get(id=area_id)  # 查询市或区的父级
            # print(parent_model)
            sub_model_list = parent_model.subs.all()
            # print(sub_model_list)

            sub_list = []
            for sub_model in sub_model_list:
                sub_list.append({'id': sub_model.id, 'name': sub_model.name})

            sub_data = {
                'id': parent_model.id,  # 父级pk
                'name': parent_model.name,  # 父级name
                'subs': sub_list  # 父级的子集
            }

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})




