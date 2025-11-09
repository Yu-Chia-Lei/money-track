from django.shortcuts import render
from django.views import View

def home(request):
    """
    網站首頁
    展示系統介紹與功能說明
    """
    return render(request, 'core/home.html')

class HomeView(View):
    def get(self, request):
        return render(request, 'core/home.html')
