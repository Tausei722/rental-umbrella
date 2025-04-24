# umbrellas/views.py

from django.views import View
from .forms import CustomForm
from django.shortcuts import render, redirect
import pdb

# ホームページのビュー
class HomeView(View):
    def get(self, request):
        return render(request, "pages/home.html")
    
# サインインフォーム
class FormView(View):
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

class SigninSuccessfullView(View):
    def get(self, request):
        return render(request, "pages/successfull_signin.html")
    
class RentalForm(View):
    def get(self, request):
        return redirect('successfull_signin')
    
class RentalSuccessfullView(View):
    def get(self, request):
        return render(request, "pages/successfull_rental.html")