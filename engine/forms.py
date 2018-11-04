from django import forms


class BottleCreateForm(forms.Form):
    name = forms.CharField(label="Nom:", max_length=80)
    solenoidValve = forms.IntegerField(label='Valve:',min_value=1,max_value=6,widget=forms.HiddenInput())
    step = forms.IntegerField(label='Position:',widget=forms.HiddenInput())
    empty = forms.BooleanField(label='Vide:',initial=False,required=False)
    image = forms.ImageField(label='Ajouter une image:',required=False)
class BottleForm(forms.Form):
    empty = forms.BooleanField(label='Vide:',required=False)
    delete = forms.BooleanField(label='Supprimer:', required=False)

