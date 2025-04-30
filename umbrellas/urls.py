# umbrellas/urls.py
from django.urls import path
from .views import HomeView, SigninView, CustomLoginView, LogoutView, RentalForm, RentalAnotherForm, LostUmbrella

urlpatterns = [
    # ホームディレクトリ
    path('', HomeView.as_view(), name='home'),
    path('form/', SigninView.as_view(), name='form'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('rental/', RentalAnotherForm.as_view(), name="rental_another"),
    path('rental/rental/<str:pk>', RentalForm.as_view(), name="rental"),
    path('lost_umbrella/', LostUmbrella.as_view(), name="lost_umbrella"),
]
