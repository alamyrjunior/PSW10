from django.urls import path, include
from . import views

urlpatterns = [
    path('cadastro/', views.cadastro, name="cadastro"),
    path('login/', views.login_view, name="login"),
    path('sair/', views.sair, name="sair"),
]