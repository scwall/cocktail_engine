from django.contrib import admin
from .models import Cocktail, Bottle, Bottles_belongs_cocktails, SolenoidValve

# Register your models here.
admin.site.register(Cocktail)
admin.site.register(Bottle)
admin.site.register(SolenoidValve)
class Bottles_belongs_cocktailsAdmin(admin.ModelAdmin):
    list_display = ('bottle_detail','cocktail_detail','dose_detail')

admin.site.register(Bottles_belongs_cocktails,Bottles_belongs_cocktailsAdmin)