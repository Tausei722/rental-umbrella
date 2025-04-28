# umbrellas/views.py

from django.views.generic import TemplateView
from .forms import CustomForm, LoginForm
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate, logout

# ホームページのビュー
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "pages/home.html"
    login_url = "/login/"
    redirect_field_name = "next"

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context["username"] = self.request.user.username
            return context

# サインインフォーム
class SigninView(TemplateView):
    template_name = "pages/form.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

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
class SigninSuccessfullView(TemplateView):
    def get(self, request):
        return render(request, "pages/successfull_signin.html")

class CustomLoginView(LoginView):
    template_name = "pages/login.html"
    authentication_form = LoginForm

    def get_success_url(self):
        success_redirect_url = self.request.GET.get("next") or "/"
        print("asdfghjh:",success_redirect_url)
        return success_redirect_url

    def post(self, request):
        form = LoginForm(data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect(self.get_success_url())

        return render(request, "pages/login.html", {"form": form})

class LogoutView(TemplateView):
    def get(self, request):
        logout(request)
        return redirect("/login/")