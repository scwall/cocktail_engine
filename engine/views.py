from django.http import HttpResponse
import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from engine.models import Cocktail, Bottle, Bottles_belongs_cocktails
# Create your views here.
def index(request):

    cocktail = Cocktail.objects.all()

    return render(request, 'index.html', {'context':cocktail})

@csrf_exempt
def selected_cocktail(request,id):

    cocktail1 = Cocktail.objects.get(id=id)
    bottles = Bottles_belongs_cocktails.objects.filter(cocktail=cocktail1)

    json_data = json.dumps({"HTTPRESPONSE": "ok"})

    return HttpResponse(json_data, mimetype="application/json")

