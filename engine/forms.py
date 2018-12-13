#!/usr/bin/python3
from django import forms
from django.forms import formset_factory

from .models import Bottle


class BottleCreateForm(forms.Form):
    """
    Form for create the bottle in bottle admin
    """
    name = forms.CharField(label="Nom:", max_length=80,
                           widget=forms.TextInput(attrs={'style': 'width:8rem'}))
    solenoidValve = forms.IntegerField(label='Valve:',
                                       min_value=1, max_value=6, widget=forms.HiddenInput())
    empty = forms.BooleanField(label='Vide:', initial=False, required=False)
    image = forms.ImageField(label='Ajouter une image:', required=False, )


class BottleChooseForm(forms.Form):
    """
    Form for selected the bottle in creation
    for the creation of the cocktail in cocktail admin
    """
    bottle = forms.ModelChoiceField(queryset=Bottle.objects.values_list('name', flat=True),
                                    label="Bouteille:", to_field_name="name")
    dose = forms.IntegerField(label='Dose:',
                              widget=forms.NumberInput(attrs={'style': 'width:3rem'}))


class CocktailMakeForm(forms.Form):
    """
        Form for create cocktail in bottle admin
    """
    name = forms.CharField(label="Nom:", max_length=80)
    description = forms.CharField(label='Description',
                                  widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}),
                                  required=False)
    image = forms.ImageField(label='Ajouter une image:', required=False)


BottleFormSet = formset_factory(BottleChooseForm, max_num=6)
