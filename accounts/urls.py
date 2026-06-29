from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('dang-ky/', views.register_view, name='register'),
    path('dang-nhap/', views.CustomLoginView.as_view(), name='login'),
    path('dang-xuat/', views.logout_view, name='logout'),
    path('ho-so/', views.profile_view, name='profile'),
    path('doi-mat-khau/', views.change_password_view, name='change_password'),
]
