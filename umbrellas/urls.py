# umbrellas/urls.py
from django.urls import path
from .views import HomeView, SigninView, SigninSuccessfullView, LoginView

urlpatterns = [
    # ホームディレクトリ
    path('', HomeView.as_view(), name='home'),
    path('form/', SigninView.as_view(), name='form'),
    path('form/successfull_signin/', SigninSuccessfullView.as_view(), name='successfull_signin'),
    path('login/', LoginView.as_view(), name='login'),
]
