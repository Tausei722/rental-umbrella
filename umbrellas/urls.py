# umbrellas/urls.py
from django.urls import path
from .views import HomeView, FormView, SigninSuccessfullView, RentalForm, RentalSuccessfullView

urlpatterns = [
    # ホームディレクトリ
    path('', HomeView.as_view(), name='home'),
    path('form/', FormView.as_view(), name='form'),
    path('form/successfull_signin/', SigninSuccessfullView.as_view(), name='successfull_signin'),
    path('rental/successfull_rental/', RentalSuccessfullView.as_view(), name='successfull_rental'),
    path('rental/<str:umbrella_key>/', RentalForm.as_view(), name='rntal_form'),
]
