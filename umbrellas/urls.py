# umbrellas/urls.py
from django.urls import path
<<<<<<< HEAD
from .views import HomeView, FormView, SigninSuccessfullView, RentalForm, RentalSuccessfullView
=======
from .views import HomeView, SigninView, SigninSuccessfullView, CustomLoginView, LogoutView
>>>>>>> develop

urlpatterns = [
    # ホームディレクトリ
    path('', HomeView.as_view(), name='home'),
    path('form/', SigninView.as_view(), name='form'),
    path('form/successfull_signin/', SigninSuccessfullView.as_view(), name='successfull_signin'),
<<<<<<< HEAD
    path('rental/successfull_rental/', RentalSuccessfullView.as_view(), name='successfull_rental'),
    path('rental/<str:umbrella_key>/', RentalForm.as_view(), name='rntal_form'),
=======
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name="logout"),
>>>>>>> develop
]
