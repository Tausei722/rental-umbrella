# umbrellas/urls.py
from django.urls import path
from .views import HomeView, FormView, SigninSuccessfullView, LoginView

urlpatterns = [
    # ホームディレクトリ
    path('home/', HomeView.as_view(), name='home'),
    path('form/', FormView.as_view(), name='form'),
    path('form/successfull_signin/', SigninSuccessfullView.as_view(), name='successfull_signin'),
    path('login/', LoginView.as_view(), name='login'),
]
