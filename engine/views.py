import time

from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
import json
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
import json

from engine.forms import BottleCreateForm, BottleForm
from engine.models import Cocktail, Bottle, Bottles_belongs_cocktails
from .tasks import make_cocktail
from celery.result import AsyncResult
from django import template



#cocktail Views is main view

@csrf_exempt
def cocktailViews(request):
    cocktails = Cocktail.objects.all().order_by('id')
    context = {'title': 'Liste des cocktails', 'cocktails': cocktails, }
    return render(request, template_name='index.html', context=context)

#makeCocktail serve for create asyncronious task, and send in jquery script for the progression bar
@csrf_exempt
def makeCocktail(request):
    if request.is_ajax():
        if 'cocktail_id' in request.POST.keys() and request.POST['cocktail_id']:
            cocktail_id = request.POST['cocktail_id']
            cocktail = Cocktail.objects.get(id=cocktail_id)
            for bottle in cocktail.bottles.all():
                print(bottle.name, " ", Bottles_belongs_cocktails.objects.get(bottle=bottle.id, cocktail=cocktail.id))
            dict_execute_cocktail = {'step': 1, 'solenoidValve': 2}
            task = make_cocktail.delay(dict_execute_cocktail)
            return JsonResponse({'task_id': task.id})

        if 'task_id' in request.POST.keys() and request.POST['task_id']:
            task_id = request.POST['task_id']
            task = AsyncResult(task_id)
            if task.info is None:
                task_info = 0
            else:
                task_info = task.result['total']
            return JsonResponse({'task_info': task_info})

@csrf_exempt
def cocktailEngineAdmin(request):
    bottles = Bottle.objects.all().order_by('id')
    if request.method == 'POST':
        bottle_create_form = BottleCreateForm(request.POST)
        bottle_form = BottleForm(request.POST)
        # check whether it's valid:
        if bottle_create_form.is_valid():
            name = bottle_create_form.cleaned_data['name']
            solenoidValve = bottle_create_form.cleaned_data['solenoidValve']
            step = bottle_create_form.cleaned_data['step']
            empty = bottle_create_form.cleaned_data['empty']
            image = bottle_create_form.cleaned_data['image']
            bottle = Bottle.objects.create(name=name,solenoidValve=solenoidValve,step=step,empty=empty,image=image)
            bottle.save()
    else:
        bottle_create_form = BottleCreateForm()
        bottle_form = BottleForm()
    context = {'bottles': bottles, 'bottle_create_form': bottle_create_form,'bottle_form':bottle_form }
    return render(request,template_name='cocktail-engine-admin/bottles.html', context=context)
@csrf_exempt
def bottleModifyParameter(request):
    if request.is_ajax():
        if 'empty' in request.POST.keys():
            print('true')
            empty = {}
            bottles = Bottle.objects.all()
            for bottle in bottles:
                empty[bottle.solenoidValve] = bottle.empty
            return JsonResponse({'empty': empty})
        return JsonResponse({'':''})