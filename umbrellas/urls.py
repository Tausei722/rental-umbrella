# umbrellas/urls.py
from django.urls import path
from .views import HomeView, SigninView, SigninSuccessfullView, CustomLoginView, LogoutView, RentalForm

urlpatterns = [
    # ホームディレクトリ
    path('', HomeView.as_view(), name='home'),
    path('form/', SigninView.as_view(), name='form'),
    path('form/successfull_signin/', SigninSuccessfullView.as_view(), name='successfull_signin'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('rental/<str:pk>', RentalForm.as_view(), name="rental"),
]
