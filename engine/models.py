from django.db import models

# Create your models here.
class Cocktail(models.Model):
    name = models.CharField(max_length=80)
    description = models.TextField()



class Bottle(models.Model):

    name = models.CharField(max_length=80)
    solenoidValve = models.IntegerField()
    step = models.IntegerField()
    empty = models.BooleanField(default=False)



class Bottles_belongs_cocktails(models.Model):

    bottle = models.ForeignKey(Bottle, on_delete=models.CASCADE)
    cocktail = models.ForeignKey(Cocktail, on_delete=models.CASCADE)
    dose = models.IntegerField()
