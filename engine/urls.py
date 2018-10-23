from django.conf.urls import url

from engine import views

urlpatterns = [

    url('', views.index, name='index'),
    url('admin', views.index, name='admin'),
    url('selected_cocktail/<int:id>',views.selected_cocktail)

]
