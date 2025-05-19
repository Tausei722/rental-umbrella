# umbrellas/views.py

from django.views.generic import TemplateView
from .forms import CustomForm, LoginForm, ReturnForm, ContactForm, MapForm
from .models import Umbrellas, CustomUser, LostComments, RentalLog
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
import smtplib
import time
from email.mime.text import MIMEText
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import CustomUser
from django.core.mail import send_mail
from datetime import datetime, timedelta

from django.conf import settings
import os
from dotenv import load_dotenv

# 404エラーページのカスタマイズ
def custom_404(request, exception):
    return render(request, "404.html", status=404)

# ホームページのビュー
class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user is None:
            context["username"] = self.request.user.username
        else:
            context["username"] = "新規ユーザー"

        try:
            if self.request.user.is_authenticated:
                rental_umbrella = Umbrellas.objects.get(borrower=self.request.user)
            else:
                rental_umbrella = None
        except ObjectDoesNotExist:
            rental_umbrella = None
        print(rental_umbrella,"cvdsfdgthryekdvc")

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
        next_url = self.request.GET.get("next") or self.request.POST.get("next")
        return next_url if next_url else "/"

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
class RentalForm(TemplateView):
    template_name = "pages/rental.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pk"] = self.kwargs.get("pk")
        context["user"] = self.request.user
        return context
    
    def get(self, request, *args, **kwargs):
        form = ReturnForm()

        if request.user.is_authenticated:
            try:
                # すでにレンタルしているかどうか仕分ける
                is_rentaled = Umbrellas.objects.get(borrower=request.user)
                if is_rentaled:
                    return render(request, "pages/rental.html", {"form": form, "is_rentaled": False, "pk": self.kwargs['pk']})
                else:
                    return render(request, "pages/rental.html", {"form": form, "is_rentaled": True, "pk": self.kwargs['pk']})
            except Umbrellas.DoesNotExist:
                # そもそもログインしてなかったら
                return render(request, "pages/rental.html", {"form": form, "is_rentaled": True, "pk": self.kwargs['pk']})

        try:
            Umbrellas.objects.get(umbrella_name=self.kwargs['pk'])
        except ObjectDoesNotExist:
            return render(request, "pages/404.html", {'form': form})

        return render(request, "pages/rental.html", {'form': form, "is_rentaled": True, "pk": self.kwargs['pk']})
    
    def post(self, request, **kwargs):
        context = self.get_context_data()
        form = ReturnForm()

        # 借りるときの処理
        if "cancel" in request.POST:
            return render(request, "pages/home.html")

        if "lend" in request.POST:
            try:
                # この画面がQRで遷移するとき絶対にログイン要求をされるのでここだけRequire使わずに手動でログイン
                try:
                    if not request.user.is_authenticated:
                        return redirect("/login/")
                except AttributeError:  # user が None か、属性がない場合
                    return redirect("/login/")
                except Exception as e:  # その他の予期しないエラー対策
                    print(f"Unexpected error: {e}")  # ログに出力
                    return redirect("/login/")
                rental_umbrella = Umbrellas.objects.get(umbrella_name=self.kwargs['pk'])
                
                # すでにborrowerがいた場合はエラーを変えす
                if rental_umbrella.borrower is not None:
                    messages.error(request, "❌ その傘はすでに借りられているか、返却されていません")
                    return redirect(request.path) 
                else:
                    rental_umbrella.borrower = CustomUser.objects.get(username=context["user"])
                    rental_umbrella.save()

                    update_user = CustomUser.objects.get(username=request.user.username)
                    update_user.update_at = datetime.now()
                    update_user.save()

                    rental_log = RentalLog.objects.create(
                        user=request.user,
                        umbrella=rental_umbrella,
                        is_rental=True
                    )

                    rental_user = request.user
                    rental_user.borrowed_umbrella = rental_umbrella
                    rental_user.save()
                    return render(request, "pages/successfull_rental.html")
            except ValueError as e:
                return redirect(request.path)

        # 返すときの処理
        elif "return" in request.POST:
            form = ReturnForm(request.POST)
            try:
                rental_umbrella = Umbrellas.objects.get(umbrella_name=self.kwargs['pk'])
            except ObjectDoesNotExist:
                return render(request, "pages/rental.html", {"is_rentaled": True})

            # 借りている人と今返却フォームを操作している人が同じか見る
            if rental_umbrella.borrower == request.user:
                if form.is_valid():
                    rental_umbrella.borrower = None
                    rental_umbrella.place = form.cleaned_data.get('place')
                    rental_umbrella.save()

                    rental_log = RentalLog.objects.create(
                        user=request.user,
                        umbrella=rental_umbrella,
                        is_rental=False
                    )

                    rental_user = request.user
                    rental_user.borrowed_umbrella = None
                    rental_user.save()
                else:
                    messages.error(request, "❌ フォームの入力内容が正しくありません")
                    return redirect(request.path)
                return render(request, "pages/successfull_return.html")
            else:
                messages.error(request, "❌ その傘は別の人に借りられています")
                return redirect(request.path)

# 数字入力で傘借りる
class RentalAnotherForm(TemplateView):
    template_name = "pages/rental_another.html"

    def get(self, request):
        form = ReturnForm()

        if request.user.is_authenticated:
            try:
                # すでにレンタルしているかどうか仕分ける
                is_rentaled = Umbrellas.objects.get(borrower=request.user)
                if is_rentaled:
                    return render(request, "pages/rental_another.html", {"form": form, "is_rentaled": False})
                else:
                    return render(request, "pages/rental_another.html", {"form": form, "is_rentaled": True})
            except Umbrellas.DoesNotExist:
                # そもそもログインしてなかったら
                return render(request, "pages/rental_another.html", {"form": form, "is_rentaled": True})

        return render(request, "pages/rental_another.html", {"form": form, "is_rentaled": True})
    
    def post(self, request):
        umbrella_name = request.POST.get('umbrella_number')
        form = ReturnForm(request.POST)

        # この画面がQRで遷移するとき絶対にログイン要求をされるのでここだけRequire使わずに手動でログイン
        try:
            if not request.user.is_authenticated:
                return redirect("/login/")
        except AttributeError:  # user が None か、属性がない場合
            return redirect("/login/")
        except Exception as e:  # その他の予期しないエラー対策
            print(f"Unexpected error: {e}")  # ログに出力
            return redirect("/login/")

        # 借りるときの処理
        if "cancel" in request.POST:
            return render(request, "pages/home.html")

        if "lend" in request.POST:
            try:
                rental_umbrella = Umbrellas.objects.get(umbrella_name=umbrella_name)
                # すでにborrowerがいた場合はエラーを変えす
                if rental_umbrella.borrower is not None:
                    messages.error(request, "❌ その傘はすでに借りられているか、返却されていません")
                    return redirect(request.path) 
                else:
                    rental_umbrella.borrower = CustomUser.objects.get(username=request.user)
                    rental_umbrella.save()

                    update_user = CustomUser.objects.get(username=request.user.username)
                    update_user.update_at = datetime.now()
                    update_user.save()

                    rental_log = RentalLog.objects.create(
                        user=request.user,
                        umbrella=rental_umbrella,
                        is_rental=True
                    )

                    rental_user = request.user
                    rental_user.borrowed_umbrella = rental_umbrella
                    rental_user.save()
                    return render(request, "pages/successfull_rental.html")
            except ObjectDoesNotExist:
                messages.error(request, "❌ 傘が見つかりませんでした！")
                return redirect(request.path)

        # 返すときの処理
        elif "return" in request.POST:
            try:
                rental_umbrella = Umbrellas.objects.get(umbrella_name=umbrella_name)
            except ObjectDoesNotExist:
                messages.error(request, "❌ 入力された番号と違います")
                return redirect(request.path)

            # 借りている人と今返却フォームを操作している人が同じか見る
            if rental_umbrella.borrower == request.user:
                if form.is_valid():
                    rental_umbrella.borrower = None
                    rental_umbrella.place = form.cleaned_data.get('place')
                    rental_umbrella.save()

                    rental_log = RentalLog.objects.create(
                        user=request.user,
                        umbrella=rental_umbrella,
                        is_rental=False
                    )
                    rental_user = request.user
                    rental_user.borrowed_umbrella = None
                    rental_user.save()
                else:
                    messages.error(request, "❌ フォームの入力内容が正しくありません")
                    return redirect(request.path)
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

# パスワード忘れのフォーム
class CustomPasswordResetView(TemplateView):
    template_name = "registration/password_reset_form.html"

    def post(self, request):
        form = request.POST.get('email')
        # トークンの作成
        user = CustomUser.objects.get(email=form)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # サーバー接続
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_user = settings.EMAIL_HOST_USER
        smtp_password = settings.EMAIL_HOST_PASSWORD

        # メール本文の作成
        email_body = """\
            こんにちは、{username} さん

            パスワードをリセットするには、以下のリンクをクリックしてください:

            {uri}

            このリンクの有効期限は1時間です。
            """
        
        email_body = email_body.format(
            username=request.user.username,
            uri=f"https://share-kasa-f551340d651d.herokuapp.com/reset/{uidb64}/{token}",
        )

        # 送信
        msg = MIMEText(email_body, "html")
        msg["Subject"] = "シェア傘アカウントのパスワードリセット"
        msg["From"] = smtp_user
        msg["To"] = form

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, [form], msg.as_string())
            server.quit()
        except smtplib.SMTPException as e:
            return render(request, "registration/password_reset_form.html", {"submit": "SMTP エラーが発生しました: {e}"})

        return render(request, "registration/password_reset_form.html", {"submit": "メールが送信されました"})
    
# お問い合わせフォームの作成
class ContactView(LoginRequiredMixin, TemplateView):
    template_name = "pages/contact.html"

    def get(self, request):
        form = ContactForm()
        return render(request, 'pages/contact.html', {"form": form})

    def post(self, request):
        form = ContactForm(request.POST)

        if form.is_valid():
            contact = form.save(commit=False)
            contact.username = request.user
            form.save()
            return render(request, 'pages/successfull_contact_form.html')
        return render(request, 'pages/contact.html', {"form": form})

class MapView(LoginRequiredMixin, TemplateView):
    template_name = "pages/map.html"

    def get(self, request):
        form = MapForm()
        return render(request, "pages/map.html", {"form": form})

    def post(self, request):
        form = MapForm(request.POST)
        if form.is_valid():
            place = form.cleaned_data.get("place")
            try:
                umbrellas = Umbrellas.objects.filter(place=place,borrower__isnull=True)
                if umbrellas is not None:
                    print(umbrellas)
                    return render(request, "pages/map.html", {"form": form, "umbrellas": umbrellas})
                else:
                    messages.success(request, "その場所に傘はありません")
            except Umbrellas.DoesNotExist:
                messages.error(request, "エラーが発生しました")
        return render(request, "pages/map.html", {"form": form})