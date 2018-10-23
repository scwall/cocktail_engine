from django.conf.urls import url

from engine import views

urlpatterns = [

    url('', views.index, name='index')
]
