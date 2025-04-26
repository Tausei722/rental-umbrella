# umbrellas/views.py

from django.views import View
from .forms import CustomForm, LoginForm
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login,authenticate

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
class CustomLoginView(LoginView):
    template_name = "pages/login.html"
    form_class = LoginForm

    def get_success_url(self):
        success_redirect_url = self.request.GET.get("next") or "/"
        print("asdfghjh:",success_redirect_url)
        return success_redirect_url

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            print(user,"ghjklgfvbjuyg",username,password)
            if user is not None:
                login(request, user)
                return redirect(self.get_success_url())
        return render(request, "pages/login.html", {"form": form})