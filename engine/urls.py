from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path

from engine import views
from engine.views import IndexViews

urlpatterns = [

    path('', IndexViews.as_view(),name='bottles'),
    path('selected_cocktail/<int:id>',views.selected_cocktail)

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
