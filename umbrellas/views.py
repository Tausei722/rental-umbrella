# umbrellas/views.py

from django.views import View
from .forms import CustomForm
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin

# ホームページのビュー
class HomeView(View, LoginRequiredMixin):
    def get(self, request):
        return render(request, "pages/home.html")
    
# サインインフォーム
class SigninView(View):
    def get(self, request):
        form = CustomForm()
        return render(request, "pages/form.html", {'form': form})

    def post(self, request):
        form = CustomForm(request.POST)
        # 入力した情報をDBにセーブし成功ページへリダイレクト
        if form.is_valid():
            form.save()
            return redirect('successfull_signin')

        # 失敗したらページにエラーメッセージを表示
        return render(request, "pages/form.html", {'form': form})

# サインイン完了画面
class SigninSuccessfullView(View):
    def get(self, request):
        return render(request, "pages/successfull_signin.html")

# ログイン画面
class LoginView(LoginView,View):
    def get(self, request):
        return render(request)