"""
URL configuration for fitness_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views
from core import views_admin

admin_ia_patterns = [
    path('', views_admin.ia_dashboard, name='ia_dashboard'),
    path('treinamento/', views_admin.treinamento_dashboard, name='treinamento_dashboard'),
    path('treinamento/upload/', views_admin.upload_documento, name='upload_documento'),
    path('treinamento/modelo/criar/', views_admin.criar_modelo, name='criar_modelo'),
    path('treinamento/api-key/gerar/', views_admin.gerar_api_key, name='gerar_api_key'),
    path('treinamento/processar-documento/<int:doc_id>/', views_admin.processar_documento, name='processar_documento'),
    path('treinamento/treinar-modelo/<int:modelo_id>/', views_admin.treinar_modelo, name='treinar_modelo'),
    path('treinamento/revogar-api-key/<str:key>/', views_admin.revogar_api_key, name='revogar_api_key'),
]

urlpatterns = [
    path('admin/ia/', include(admin_ia_patterns)),  # URLs do admin da IA
    path('admin/', admin.site.urls),  # Admin padrão do Django
    path('', views.dashboard, name='dashboard'),
    path('registro/', views.registro, name='registro'),
    path('perfil/', views.perfil, name='perfil'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('alimentos-personalizados/', views.alimentos_personalizados, name='alimentos_personalizados'),
    path('alimentos-personalizados/excluir/<int:alimento_id>/', views.excluir_alimento_personalizado, name='excluir_alimento_personalizado'),
]
