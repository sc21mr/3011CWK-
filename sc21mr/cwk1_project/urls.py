"""
URL configuration for cwk1_project project.

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
from django.urls import path
from news_agency_app.views import loginURL, logoutURL, storiesURL, delete_storyURL

urlpatterns = [
    path('admin', admin.site.urls),
    path('api/login', loginURL, name='login'),
    path('api/logout', logoutURL, name='logout'),
    path('api/stories', storiesURL, name='stories'),
    path('api/stories/<str:key>', delete_storyURL, name='delete_story')
]
