from django.contrib import admin
from .models import Cocktail, Bottle, Bottles_belongs_cocktails

# Register your models here.
admin.site.register(Cocktail)
admin.site.register(Bottle)
class Bottles_belongs_cocktailsAdmin(admin.ModelAdmin):
    list_display = ('Recipe_of_cocktails',)
admin.site.register(Bottles_belongs_cocktails,Bottles_belongs_cocktailsAdmin)