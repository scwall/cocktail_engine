import time

from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
import json
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.generic import ListView
import json

from engine.forms import BottleCreateForm, BottleFormSet, CocktailMakeForm
from engine.models import Cocktail, Bottle, Bottles_belongs_cocktails, SolenoidValve
from .tasks import make_cocktail
from celery.result import AsyncResult
from django import template


# cocktail Views is main view
@ensure_csrf_cookie
def cocktailViews(request):
    bottles = Bottle.objects.all().order_by('name')
    cocktails = Cocktail.objects.all().order_by('id')
    if request.method == "GET":
        if request.GET.get('bottle'):
            bottle = request.GET.get('bottle')
            cocktails = Cocktail.objects.filter(bottles_belongs_cocktails__bottle_id=bottle)
        if request.GET.get('name'):
            name = request.GET.get('name')
            cocktails = Cocktail.objects.filter(name__icontains=name)

    context = {'title': 'Liste des cocktails', 'cocktails': cocktails, 'bottles': bottles}

    return render(request, template_name='index.html', context=context)


# makeCocktail serve for create asyncronious task, and send in jquery script for the progression bar

def makeCocktail(request):
    if request.is_ajax():
        if 'cocktail_id' in request.POST.keys() and request.POST['cocktail_id']:
            cocktail_id = request.POST['cocktail_id']
            cocktail = Cocktail.objects.get(id=cocktail_id)

            if cocktail.bottles.filter(empty=True) or not cocktail.bottles.all():
                return JsonResponse({'task_id': 'error'})


            else:
                list_execute_cocktail = [{'step': SolenoidValve.objects.get(number=bottle.solenoid_valve_id).step,
                                          'first_pin': SolenoidValve.objects.get(number=bottle.solenoid_valve_id).first_pin,
                                          'second_pin':SolenoidValve.objects.get(number=bottle.solenoid_valve_id).second_pin,
                                          'solenoidvalve': bottle.solenoid_valve_id,
                                          'dose': Bottles_belongs_cocktails.objects.get(bottle=bottle.id,
                                                                                        cocktail=cocktail.id).dose}
                                         for bottle in cocktail.bottles.all()]
                print('execute ', list_execute_cocktail)
                task = make_cocktail.delay(list_execute_cocktail)
                return JsonResponse({'task_id': task.id})

        if 'task_id' in request.POST.keys() and request.POST['task_id']:
            task_id = request.POST['task_id']
            task = AsyncResult(task_id)
            if task.info is None:
                task_info = 0
            else:
                task_info = task.result['total']
            return JsonResponse({'task_info': task_info})

@ensure_csrf_cookie
def bottleEngineAdmin(request):
    valves = SolenoidValve.objects.all().order_by('number')

    if request.method == 'GET':
        if request.GET.get('deleteBottle'):
            delete_bottle = request.GET.get('deleteBottle')
            Cocktail.objects.filter(bottles_belongs_cocktails__bottle_id=delete_bottle).delete()
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

def bottleModifyParameter(request):
    if request.is_ajax():
        if 'empty' in request.POST.keys() and request.POST['empty'] and 'solenoidValve' in request.POST.keys() and \
                request.POST['solenoidValve']:
            empty = (lambda boolean: True if 'true' == boolean else False)(request.POST['empty'])
            solenoidValve = request.POST['solenoidValve']
            Bottle.objects.filter(solenoid_valve__number=solenoidValve).update(empty=empty)

            return JsonResponse({'empty': 'ok'})
        if 'step' in request.POST.keys() and request.POST['step'] and 'solenoidValve' in request.POST.keys() and \
                request.POST['solenoidValve']:
            step = request.POST['step']
            solenoidValve = request.POST['solenoidValve']
            SolenoidValve.objects.filter(number=solenoidValve).update(step=step)
            return JsonResponse({'step': 'ok'})
        return JsonResponse({'': ''})

@ensure_csrf_cookie
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
