#!/usr/bin/python3
from django.urls import path

from engine.views import cocktail_views, bottle_engine_admin, make_the_cocktail, bottle_modify_parameter, \
    cocktail_engine_admin

app_name = 'engine'
urlpatterns = [

    path('', cocktail_views,
         name='cocktail_views'),

    path('make-cocktail', make_the_cocktail,
         name='make_the_cocktail'),

    path('bottle-engine-admin', bottle_engine_admin,
         name='bottle_engine_admin'),

    path('bottle-modify-parameter', bottle_modify_parameter,
         name='bottle_modify_parameter'),

    path('cocktail-engine-admin', cocktail_engine_admin,
         name='cocktail_engine_admin'),

]
