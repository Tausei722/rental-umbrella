# umbrellas/views.py

from django.views.generic import TemplateView
from .forms import CustomForm, LoginForm
from .models import Umbrellas, CustomUser
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

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
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            login(request, user)
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

# ログアウトの処理
class LogoutView(TemplateView):
    def get(self, request):
        logout(request)
        return redirect("/login/")

# QRで傘借りる
class RentalForm(LoginRequiredMixin, TemplateView):
    template_name = "pages/rental.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pk"] = self.kwargs.get("pk")
        context["user"] = self.request.user
        return context
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def post(self, request, **kwargs):
        context = self.get_context_data()
        try:
            rental_umbrella = Umbrellas.objects.get(umbrella_name=self.kwargs['pk'])
            
            if rental_umbrella.borrower is not None:
                messages.error(request, "❌ その傘はすでに借りられているか、返却されていません")
                return redirect(request.path) 
            else:
                rental_umbrella.borrower = CustomUser.objects.get(username=context["user"])
                rental_umbrella.save()
        except ValueError as e:
            return redirect(request.path)


        return render(request, "pages/successfull_rental.html")

# 数字入力で傘借りる{'view': <umbrellas.views.RentalForm object at 0x7f76e2a3a710>, 'pk': '44c6b9e5d9ca9760', 'user': <SimpleLazyObject: <CustomUser: rio>>}
class RentalAnotherForm(LoginRequiredMixin, TemplateView):
    template_name = "pages/rental_another.html"

    def get(self, request):
         return render(request, "pages/rental_another.html")
    
    def post(self, request):
        umbrella_name = request.POST.get('umbrella_number')

        try:
            umbrella = Umbrellas.objects.get(umbrella_name=umbrella_name)
        except ObjectDoesNotExist:
            messages.error(request, "❌ 傘が見つかりませんでした！")
            return redirect(request.path)
        
        if umbrella.borrower is not None:
            messages.error(request, "❌ その傘はすでに借りられているか、返却されていません")
            return redirect(request.path) 
        else:
            url = "rental/" + str(umbrella_name)
            print(url)
            return redirect(url)