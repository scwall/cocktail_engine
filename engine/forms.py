from django import forms


class BottleForm(forms.Form):
    name = forms.CharField(label="Title", max_length=80)
    solenoidValve = forms.IntegerField(label='Solenoid valve')
    step = forms.IntegerField(label='Solenoid valve')
    empty = forms.BooleanField(label='empty')
    image = forms.ImageField(label='image')