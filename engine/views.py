from django.http import HttpResponse
import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView

from engine.models import Cocktail, Bottle, Bottles_belongs_cocktails
# Create your views here.
class CocktailViews(ListView):
    model = Cocktail
    context_object_name = "cocktails"
    template_name = "index.html"

@csrf_exempt
def selected_cocktail(request,id):

    cocktail1 = Cocktail.objects.get(id=6)
    bottle = cocktail1.bottles_set.all()
    bottles = Bottles_belongs_cocktails.objects.filter(cocktail=cocktail1)

    json_data = json.dumps({"HTTPRESPONSE": "ok"})

    return HttpResponse(json_data, mimetype="application/json")

