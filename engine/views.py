import platform

from celery.result import AsyncResult
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

from cocktail_engine.celery import app
from engine.forms import BottleCreateForm, BottleFormSet, CocktailMakeForm
from engine.models import Cocktail, Bottle, BottlesBelongsCocktails, SolenoidValve
from .tasks import make_cocktail


# cocktail Views is main view
@ensure_csrf_cookie
def cocktail_views(request):
    """
    The main view that shows the cocktail list. This is filtered if a bottle is empty
    """
    bottles = Bottle.objects.all().order_by('name')
    cocktails = Cocktail.objects.all()\
        .exclude(bottlesbelongscocktails__bottle__empty=True)\
        .order_by('name')
    if request.method == "GET":
        if request.GET.get('bottle'):
            bottle = request.GET.get('bottle')
            cocktails = Cocktail.objects.\
                filter(bottlesbelongscocktails__bottle_id=bottle)\
                .exclude(bottlesbelongscocktails__bottle__empty=True)\
                .order_by('name')
        if request.GET.get('name'):
            name = request.GET.get('name')
            cocktails = Cocktail.objects.filter(name__icontains=name)\
                .exclude(bottlesbelongscocktails__bottle__empty=True)\
                .order_by('name')

    context = {'title': 'Liste des cocktails', 'cocktails': cocktails, 'bottles': bottles}

    return render(request, template_name='index.html', context=context)


def make_the_cocktail(request):
    """
    ajax request only
     make_the_cocktail serve for create asyncronious
     task, and send in jquery script for the progression bar
    :return: json response with task full, id info, total or task error
    """

    i = app.control.inspect()
    if request.is_ajax():
        if 'cocktail_id' in request.POST.keys() and request.POST['cocktail_id']:
            cocktail_id = request.POST['cocktail_id']
            cocktail = Cocktail.objects.get(id=cocktail_id)
            if cocktail.bottles.filter(empty=True) or not cocktail.bottles.all():
                return JsonResponse({'task_id': 'error'})

            if i.active()['celery@' + platform.node()]:
                return JsonResponse({'task_id': 'full'})

            list_execute_cocktail = \
                [{'step': SolenoidValve.objects.get(number=bottle.solenoid_valve_id).step,
                  'first_pin': SolenoidValve.objects.get(
                      number=bottle.solenoid_valve_id).first_pin,
                  'second_pin': SolenoidValve.objects.get(
                      number=bottle.solenoid_valve_id).second_pin,
                  'solenoidvalve': bottle.solenoid_valve_id,
                  'dose': BottlesBelongsCocktails.objects.get(bottle=bottle.id,
                                                              cocktail=cocktail.id).dose}
                 for bottle in cocktail.bottles.all()]
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
        return JsonResponse({'error': 'bad request'}, status=400)
    return HttpResponse('bad request', status=400)


@ensure_csrf_cookie
def bottle_engine_admin(request):
    """
    View for delete and create bottle, and show step and if bottle is empty

    """
    valves = SolenoidValve.objects.all().order_by('number')

    if request.method == 'GET':
        if request.GET.get('deleteBottle'):
            delete_bottle = request.GET.get('deleteBottle')
            Cocktail.objects.filter(bottlesbelongscocktails__bottle_id=delete_bottle).delete()
            Bottle.objects.filter(id=delete_bottle).delete()
            return HttpResponseRedirect(reverse('engine:bottle_engine_admin'))

    if request.method == 'POST':
        bottle_create_form = BottleCreateForm(request.POST, request.FILES)
        # check whether it's valid:
        if bottle_create_form.is_valid():
            bottle = Bottle.objects.filter(
                solenoid_valve=bottle_create_form.cleaned_data['solenoidValve'])
            if not bottle.exists():
                bottle = Bottle.objects.create(
                    name=bottle_create_form.cleaned_data['name'],
                    empty=bottle_create_form.cleaned_data['empty'],
                    image=bottle_create_form.cleaned_data['image'],
                    solenoid_valve=SolenoidValve.objects.get(
                        number=bottle_create_form.cleaned_data['solenoidValve']))
                bottle.save()
                return HttpResponseRedirect(reverse('engine:bottle_engine_admin'))

    else:
        bottle_create_form = BottleCreateForm()
    context = {'bottles': valves, 'bottle_create_form': bottle_create_form, }

    return render(request, template_name='cocktail-engine-admin/bottles.html', context=context)


def bottle_modify_parameter(request):
    """
    Request ajax using for modify empty and step in database
    :return: empty 'ok' for confirm the request is executed
    """
    if request.is_ajax():
        if 'empty' in request.POST.keys() and \
                request.POST['empty'] and 'solenoidValve' \
                in request.POST.keys() and \
                request.POST['solenoidValve']:
            empty = bool(str.lower(request.POST['empty']) == 'true')
            solenoid_valve = request.POST['solenoidValve']
            Bottle.objects.filter(
                solenoid_valve__number=solenoid_valve).update(empty=empty)

            return JsonResponse({'empty': 'ok'})
        if 'step' in request.POST.keys() and \
                request.POST['step'] and 'solenoidValve' in \
                request.POST.keys() and \
                request.POST['solenoidValve']:
            step = request.POST['step']
            solenoid_valve = request.POST['solenoidValve']
            SolenoidValve.objects.filter(number=solenoid_valve).update(step=step)
            return JsonResponse({'step': 'ok'})
        return JsonResponse({'error': 'bad request'}, status=400)

    return HttpResponse('bad request', status=400)


@ensure_csrf_cookie
def cocktail_engine_admin(request):
    """
    View for create and delete cocktail
    """
    cocktails = Cocktail.objects.filter().all()
    cocktail_make_form = CocktailMakeForm()
    if request.method == 'GET':
        if request.GET.get('deleteCocktail'):
            delete_cocktail = request.GET.get('deleteCocktail')
            Cocktail.objects.filter(id=delete_cocktail).delete()
            return HttpResponseRedirect(reverse('engine:cocktail_engine_admin'))

    if request.method == 'POST':
        bottle_form_set = BottleFormSet(request.POST)
        cocktail_make_form = CocktailMakeForm(request.POST, request.FILES)
        if cocktail_make_form.is_valid() and bottle_form_set.is_valid():
            cocktail = Cocktail.objects.create(
                name=cocktail_make_form.cleaned_data.get('name'),
                description=cocktail_make_form.cleaned_data.get('description'),
                image=cocktail_make_form.cleaned_data.get('image'))

            for bottle_data in bottle_form_set:
                bottle = Bottle.objects.get(name=bottle_data.cleaned_data.get('bottle'))
                bottles_belongs_cocktails = BottlesBelongsCocktails(
                    bottle=bottle, cocktail=cocktail,
                    dose=bottle_data.cleaned_data.get('dose'))
                bottles_belongs_cocktails.save()

    else:
        bottle_form_set = BottleFormSet()
    context = {'bottle_form_set': bottle_form_set,
               'cocktail_make_form': cocktail_make_form,
               'cocktails': cocktails}

    return render(request, template_name='cocktail-engine-admin/cocktails.html', context=context)
