from django.views import View
from django.shortcuts import render

# ホームページのビュー
class HomeView(View):
    def get(self, request):
        return render(request, "pages/home.html")

class FormView(View):
    def form(self, request):
        return render(request, "pages/form.html")