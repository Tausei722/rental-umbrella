# umbrellas/urls.py
from django.urls import path
from .views import HomeView, SigninView, CustomLoginView, LogoutView, RentalForm, RentalAnotherForm, LostUmbrella, ContactView, CustomPasswordResetView, MapView
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ホームディレクトリ
    path('', HomeView.as_view(), name='home'),
    path('form/', SigninView.as_view(), name='form'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('rental/', RentalAnotherForm.as_view(), name="rental_another"),
    path('rental/rental/<str:pk>', RentalForm.as_view(), name="rental"),
    path('lost_umbrella/', LostUmbrella.as_view(), name="lost_umbrella"),
    path('contact/', ContactView.as_view(), name="contact"),
    path('map/', MapView.as_view(), name="map"),

    # パスワード再設定フォーム
    path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),  # ✅ リセットフォーム
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),  # ✅ 送信完了画面
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),  # ✅ 新しいパスワード入力
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),  # ✅ 完了画面
]
