import time

from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
import json
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
import json

from engine.forms import BottleCreateForm, BottleFormSet, CocktailMakeForm
from engine.models import Cocktail, Bottle, Bottles_belongs_cocktails, SolenoidValve
from .tasks import make_cocktail
from celery.result import AsyncResult
from django import template


# cocktail Views is main view

@csrf_exempt
def cocktailViews(request):
    cocktails = Cocktail.objects.all().order_by('id')
    bottles = Bottle.objects.all().order_by('name')

    if request.method == "GET":
        if request.GET.get('bottle'):
            bottle = request.GET.get('bottle')
            cocktails = Cocktail.objects.filter(bottles_belongs_cocktails__bottle_id=bottle)

    context = {'title': 'Liste des cocktails', 'cocktails': cocktails, 'bottles': bottles}

    return render(request, template_name='index.html', context=context)


# makeCocktail serve for create asyncronious task, and send in jquery script for the progression bar
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
def bottleEngineAdmin(request):
    valves = SolenoidValve.objects.all().order_by('number')

    if request.method == 'GET':
        if request.GET.get('deleteBottle'):
            delete_bottle = request.GET.get('deleteBottle')
            Bottle.objects.filter(id=delete_bottle).delete()
            return HttpResponseRedirect(reverse('engine:bottleEngineAdmin'))

    if request.method == 'POST':
        bottle_create_form = BottleCreateForm(request.POST, request.FILES)
        # check whether it's valid:
        if bottle_create_form.is_valid():
            bottle = Bottle.objects.filter(solenoid_valve=bottle_create_form.cleaned_data['solenoidValve'])
            if not bottle.exists():
                bottle = Bottle.objects.create(name=bottle_create_form.cleaned_data['name'],
                                               empty=bottle_create_form.cleaned_data['empty'],
                                               image=bottle_create_form.cleaned_data['image'],
                                               solenoid_valve=SolenoidValve.objects.get(
                                                   number=bottle_create_form.cleaned_data['solenoidValve']))
                bottle.save()
                return HttpResponseRedirect(reverse('engine:bottleEngineAdmin'))

    else:
        bottle_create_form = BottleCreateForm()
    context = {'bottles': valves, 'bottle_create_form': bottle_create_form, }

    return render(request, template_name='cocktail-engine-admin/bottles.html', context=context)


@csrf_exempt
def bottleModifyParameter(request):
    if request.is_ajax():
        if 'empty' in request.POST.keys() and request.POST['empty'] and 'solenoidValve' in request.POST.keys() and \
                request.POST['solenoidValve']:
            empty = (lambda boolean: True if 'true' == boolean else False)(request.POST['empty'])
            solenoidValve = request.POST['solenoidValve']
            Bottle.objects.filter(solenoid_valve=solenoidValve).update(empty=empty)
            return JsonResponse({'empty': 'ok'})
        if 'step' in request.POST.keys() and request.POST['step'] and 'solenoidValve' in request.POST.keys() and \
                request.POST['solenoidValve']:
            step = request.POST['step']
            solenoidValve = request.POST['solenoidValve']
            SolenoidValve.objects.filter(number=solenoidValve).update(step=step)
            return JsonResponse({'empty': 'ok'})
        return JsonResponse({'': ''})


@csrf_exempt
def cocktailEngineAdmin(request):
    cocktails = Cocktail.objects.filter().all()
    cocktail_make_form = CocktailMakeForm()
    if request.method == 'GET':
        if request.GET.get('deleteCocktail'):
            deleteCocktail = request.GET.get('deleteCocktail')
            Cocktail.objects.filter(id=deleteCocktail).delete()
            return HttpResponseRedirect(reverse('engine:cocktailEngineAdmin'))

    if request.method == 'POST':
        bottle_form_set = BottleFormSet(request.POST)
        cocktail_make_form = CocktailMakeForm(request.POST, request.FILES)

        if cocktail_make_form.is_valid() and bottle_form_set.is_valid():
            cocktail = Cocktail.objects.create(name=cocktail_make_form.cleaned_data.get('name'),
                                               description=cocktail_make_form.cleaned_data.get('description'),
                                               image=cocktail_make_form.cleaned_data.get('image'))

            for bottle_data in bottle_form_set:
                bottle = Bottle.objects.get(name=bottle_data.cleaned_data.get('bottle'))
                bottles_belongs_cocktails = Bottles_belongs_cocktails(bottle=bottle, cocktail=cocktail,
                                                                      dose=bottle_data.cleaned_data.get('dose'))
                bottles_belongs_cocktails.save()

    else:
        bottle_form_set = BottleFormSet()
    context = {'bottle_form_set': bottle_form_set, 'cocktail_make_form': cocktail_make_form, 'cocktails': cocktails}

    return render(request, template_name='cocktail-engine-admin/cocktails.html', context=context)
