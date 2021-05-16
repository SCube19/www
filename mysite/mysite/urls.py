"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from app.views import indexView, indexView, addFileView, addDirectoryView, deleteDirectory,\
     deleteFile, loginView, logout, resultAction, showFile, resetFile, runFramaAdv, chooseProver, setFlags, makeFiles

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', indexView),
    path('index/<int:refresh>/', indexView),
    url('showFile/', showFile),
    path('addFile/', addFileView),
    path('addDirectory/', addDirectoryView),
    url('deleteDirectory/', deleteDirectory),
    url('deleteFile/', deleteFile),
    path('resetFile/', resetFile),
    path('runFrama/<int:id>', runFramaAdv),
    path('chooseProver/', chooseProver),
    path('setFlags/', setFlags),
    path('login/', loginView),
    path('logout/', logout),
    url('resultAction/', resultAction),
    url('makeFiles/', makeFiles)
]
