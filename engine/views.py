import time

from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
import json
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
import json
from engine.models import Cocktail, Bottle, Bottles_belongs_cocktails
from .tasks import make_cocktail
from celery.result import AsyncResult
# Create your views here.
@csrf_exempt
def cocktailViews(request):
    cocktails = Cocktail.objects.all()
    paginator = Paginator(cocktails, 6)
    if request.method == 'GET':
        page = request.GET.get('page')
        cocktails_paginator= paginator.get_page(number=page)
        context = {'title':'Liste des cocktails','cocktails': cocktails_paginator,}
        return render(request,template_name='index.html',context=context)

    if request.is_ajax():
        if 'switch_nav' in request.POST.keys() and request.POST['switch_nav'] == 'load':
            page = request.POST['page']
            cocktails_paginator = paginator.get_page(number=page[6:])
            paginator_switch = {}
            if cocktails_paginator.has_next():
                paginator_switch['page_next'] = str(cocktails_paginator.has_next())
                paginator_switch['location_next'] = reverse('engine:cocktailViews') + '?page={}'.format(
                    cocktails_paginator.next_page_number()),
            if cocktails_paginator.has_previous():
                paginator_switch['page_previous'] = str(cocktails_paginator.has_previous())
                paginator_switch['location_previous'] = reverse('engine:cocktailViews') + '?page={}'.format(
                    cocktails_paginator.previous_page_number())
            return JsonResponse(paginator_switch)
        return JsonResponse({'error':'error'})

@csrf_exempt
def makeCocktail(request):
    if request.is_ajax():
        if 'cocktail_id' in request.POST.keys() and request.POST['cocktail_id']:
            cocktail_id = request.POST['cocktail_id']
            cocktail = Cocktail.objects.get(id=cocktail_id)
            for bottle in cocktail.bottles.all():
                print(bottle.name, " ", Bottles_belongs_cocktails.objects.get(bottle=bottle.id, cocktail=cocktail.id))
            job = make_cocktail.delay(3,3)
            print(job.id)
            time.sleep(5)
            task = AsyncResult(job.id)
            print(task.state)


        return JsonResponse({'foo': 'bar'})



def cocktailEngineAdmin(request):
    pass


