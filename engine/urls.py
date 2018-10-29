from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path

from engine import views
from engine.views import cocktailViews, cocktailEngineAdmin
app_name = 'engine'
urlpatterns = [

    path('', cocktailViews, name='cocktailViews'),
    path('Cocktail-engine-admin/',cocktailEngineAdmin,name='cocktailEngineAdmin'),
    path('selected_cocktail/<int:id>',views.selected_cocktail)

]