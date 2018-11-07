from django import forms
from django.forms import ModelForm
from django.forms import formset_factory
from .models import Bottle
class BottleCreateForm(forms.Form):
    name = forms.CharField(label="Nom:", max_length=80)
    solenoidValve = forms.IntegerField(label='Valve:',min_value=1,max_value=6,widget=forms.HiddenInput())
    step = forms.IntegerField(label='Position:',widget=forms.HiddenInput())
    empty = forms.BooleanField(label='Vide:',initial=False,required=False)
    image = forms.ImageField(label='Ajouter une image:',required=False)
class BottleChooseForm(forms.Form):
    bottle  =forms.ModelChoiceField(queryset=Bottle.objects.values_list('name', flat=True).order_by('name'),label="Bouteille:")
    dose = forms.IntegerField(label='Dose:',widget=forms.NumberInput(attrs={'style':'width:3rem'}))

class CocktailMakeForm(forms.Form):
    name = forms.CharField(label="Nom:", max_length=80)
    image = forms.ImageField(label='Ajouter une image:',required=False)

bottle_group =formset_factory(BottleChooseForm, max_num=6)


