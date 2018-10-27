from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path

from engine import views
from engine.views import CocktailViews

urlpatterns = [

    path('', CocktailViews.as_view(), name='bottles'),
    path('selected_cocktail/<int:id>',views.selected_cocktail)

]