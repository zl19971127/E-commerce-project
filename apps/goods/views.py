from django.shortcuts import render
from django.views import View


class ListView(View):
    def get(self,request):
        return render(request,"list.html")