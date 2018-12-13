#!/usr/bin/python3
from django.contrib import admin
from .models import Cocktail, Bottle, BottlesBelongsCocktails, SolenoidValve

# Register your models here.
admin.site.register(Cocktail)
admin.site.register(Bottle)
admin.site.register(SolenoidValve)


class BottlesBelongsCocktailsAdmin(admin.ModelAdmin):
    list_display = ('bottle_detail', 'cocktail_detail', 'dose_detail')


admin.site.register(BottlesBelongsCocktails, BottlesBelongsCocktailsAdmin)
