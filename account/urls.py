"""bluerun URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^login/' , login , name = "login"),
    url(r'^signup/' , signup , name = "signup"),
    url(r'^forgot_password/' , forgot_password , name = "forgot_password"),
    url(r'^reset/(?P<id>\d+)/(?P<otp>\d{4})/$', set_password, name='set_password'),
    url(r'^(?P<id>\d+)/logout/' , logout , name = "logout"),
    url(r'^(?P<id>\d+)/reset_password/' , reset_password , name = "reset_password"),
    url(r'^activate_account/(?P<id>\d+)/(?P<otp>\d{4})/$' , activate_account , name = "activate_account"),
]
