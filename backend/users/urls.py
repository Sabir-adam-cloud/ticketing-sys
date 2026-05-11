from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('inscription/', views.register, name='register'),
    path('connexion/', views.login_choice, name='login'),
    path('connexion/<str:role>/', views.SupportLoginView.as_view(), name='role_login'),
    path('deconnexion/', views.LogoutView.as_view(), name='logout'),
    path('profil/', views.profile, name='profile'),
]
