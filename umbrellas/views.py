# umbrellas/views.py

from django.views.generic import TemplateView
from .forms import CustomForm, LoginForm
from .models import Umbrellas, CustomUser, LostComments
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.views import PasswordResetView
import smtplib
from django.conf import settings
import os
from dotenv import load_dotenv

# ホームページのビュー
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "pages/home.html"
    login_url = "/login/"
    redirect_field_name = "next"

    def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context["username"] = self.request.user.username

            try:
                rental_umbrella = Umbrellas.objects.get(borrower=self.request.user)
            except ObjectDoesNotExist:
                rental_umbrella = None
            context["rental_umbrella"] = rental_umbrella
            return context

# サインインフォーム
class SigninView(TemplateView):
    template_name = "pages/form.html"

    def dispatch(self, request, *args, **kwargs):
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
            return render(request, "pages/successfull_signin.html")

        # 失敗したらページにエラーメッセージを表示
        return render(request, "pages/form.html", {'form': form})

class CustomLoginView(LoginView):
    template_name = "pages/login.html"
    authentication_form = LoginForm

    def get_success_url(self):
        success_redirect_url = self.request.GET.get("next") or "/"
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
        return render(request, "pages/logout.html")
    
    def post(self, request):
        if request.POST.get('logout'):
            logout(request)
            return render(request, "pages/successfull_logout.html")
        return render(request, "pages/home.html", {"logout": True})

# QRで傘借りる
class RentalForm(LoginRequiredMixin, TemplateView):
    template_name = "pages/rental.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pk"] = self.kwargs.get("pk")
        context["user"] = self.request.user
        return context
    
    def get(self, request, *args, **kwargs):
        try:
            Umbrellas.objects.get(umbrella_name=self.kwargs['pk'])
        except ObjectDoesNotExist:
            return render(request, "pages/404.html")

        # よくないけど借りてる傘を取得しようとしてなかったらエラーを出させて今のページにリダイレクト
        try:
            is_rentaled = Umbrellas.objects.get(borrower=request.user)
        except ObjectDoesNotExist:
            return render(request, "pages/rental.html", {"is_rentaled": True, "pk": self.kwargs['pk']})

        return render(request, "pages/rental.html", {"is_rentaled": False, "pk": self.kwargs['pk']})
    
    def post(self, request, **kwargs):
        context = self.get_context_data()

        # 借りるときの処理
        if "cancel" in request.POST:
            return render(request, "pages/home.html")

        if "lend" in request.POST:
            try:
                rental_umbrella = Umbrellas.objects.get(umbrella_name=self.kwargs['pk'])
                
                # すでにborrowerがいた場合はエラーを変えす
                if rental_umbrella.borrower is not None:
                    messages.error(request, "❌ その傘はすでに借りられているか、返却されていません")
                    return redirect(request.path) 
                else:
                    rental_umbrella.borrower = CustomUser.objects.get(username=context["user"])
                    rental_umbrella.save()
                    return render(request, "pages/successfull_rental.html")
            except ValueError as e:
                return redirect(request.path)

        # 返すときの処理
        elif "return" in request.POST:
            try:
                rental_umbrella = Umbrellas.objects.get(umbrella_name=self.kwargs['pk'])
            except ObjectDoesNotExist:
                return render(request, "pages/rental.html", {"is_rentaled": True})

            # 借りている人と今返却フォームを操作している人が同じか見る
            if rental_umbrella.borrower == request.user:
                rental_umbrella.borrower = None
                return render(request, "pages/successfull_return.html")
            else:
                messages.error(request, "❌ その傘は別の人に借りられています")
                return redirect(request.path)

# 数字入力で傘借りる
class RentalAnotherForm(LoginRequiredMixin, TemplateView):
    template_name = "pages/rental_another.html"

    def get(self, request):
        # よくないけど借りてる傘を取得しようとしてなかったらエラーを出させて今のページにリダイレクト
        try:
            is_rentaled = Umbrellas.objects.get(borrower=request.user)
        except ObjectDoesNotExist:
            return render(request, "pages/rental_another.html", {"is_rentaled": True})

        return render(request, "pages/rental_another.html", {"is_rentaled": False})
    
    def post(self, request):
        umbrella_name = request.POST.get('umbrella_number')

        # 借りるときの処理
        if "cancel" in request.POST:
            return render(request, "pages/home.html")

        if "lend" in request.POST:
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
                return redirect(url)

        # 返すときの処理
        elif "return" in request.POST:
            try:
                rental_umbrella = Umbrellas.objects.get(umbrella_name=umbrella_name)
            except ObjectDoesNotExist:
                messages.error(request, "❌ 入力された番号と違います")
                return redirect(request.path)

            # 借りている人と今返却フォームを操作している人が同じか見る
            if rental_umbrella.borrower == request.user:
                rental_umbrella.borrower = None
                rental_umbrella.save()
                return render(request, "pages/successfull_return.html")
            else:
                messages.error(request, "❌ その傘は別の人に借りられています")
                return redirect(request.path)

# 紛失した傘の送信フォーム
class LostUmbrella(LoginRequiredMixin, TemplateView):
    template_name = "pages/lost_umbrella.html"

    def get(self, request):
        # よくないけど借りてる傘を取得しようとしてなかったらエラーを出させて今のページにリダイレクト
        try:
            is_rentaled = Umbrellas.objects.get(borrower=request.user)
        except ObjectDoesNotExist:
            return render(request, "pages/lost_umbrella.html", {"is_rentaled": False})

        return render(request, "pages/lost_umbrella.html", {"is_rentaled": True})
    
    def post(self, request):
        lost_reason = request.POST.get('lost-reason')
        where_lost = request.POST.get('where-lost')
        lost_other = request.POST.get('lost-other')

        try:
            if lost_reason and where_lost:
                LostComments.objects.create(
                    reason = lost_reason,
                    where_lost = where_lost,
                    other = lost_other,
                    who_lost = request.user
                )

            lost_umbrella = Umbrellas.objects.get(borrower=request.user)
            lost_umbrella.borrower = None
            lost_umbrella.is_lost = True
            lost_umbrella.save()

            return render(request, "pages/successfull_lost_form.html")
        except ObjectDoesNotExist:
                messages.error(request, "❌ その傘は別の人に借りられています")
                return redirect(request.path)
        
from django.core.mail import send_mail
from django.contrib.auth.views import PasswordResetView
from django.conf import settings
# パスワード忘れのフォーム
class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        send_mail(
            "パスワードリセットのお知らせ",
            "以下のリンクをクリックしてパスワードをリセットしてください。",
            settings.EMAIL_HOST_USER,
            [form.cleaned_data["email"]],
            fail_silently=False,
        )
        print(settings.EMAIL_HOST_USER,"メール")
        return super().form_valid(form)