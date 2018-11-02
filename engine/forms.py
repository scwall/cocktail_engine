from django import forms


class BottleForm(forms.Form):
    name = forms.CharField(label="Nom:", max_length=80)
    # solenoidValve = forms.IntegerField(label='Valve:',min_value=1,max_value=6)
    step = forms.IntegerField(label='Position:')
    empty = forms.BooleanField(label='Vide:',initial=False,required=False)
    image = forms.ImageField(label='Ajouter une image:',required=False)