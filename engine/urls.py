from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path

from engine import views
from engine.views import cocktailViews, cocktailEngineAdmin,makeCocktail
app_name = 'engine'
urlpatterns = [

    path('', cocktailViews, name='cocktailViews'),
    path('make-cocktail',makeCocktail,name='makeCocktail'),
    path('cocktail-engine-admin',cocktailEngineAdmin,name='cocktailEngineAdmin'),

]