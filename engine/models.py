from django.db import models

# Create your models here.

class Bottle(models.Model):

    name = models.CharField(max_length=80)
    solenoidValve = models.IntegerField()
    step = models.IntegerField()
    empty = models.BooleanField(default=False)
    image = models.ImageField(upload_to='bottle_picture')
class Cocktail(models.Model):

    name = models.CharField(max_length=80)
    description = models.TextField()
    bottles = models.ManyToManyField(Bottle, through='Bottles_belongs_cocktails')
    image = models.ImageField(upload_to='cocktail_picture')


class Bottles_belongs_cocktails(models.Model):

    bottle = models.ForeignKey(Bottle, on_delete=models.CASCADE)
    cocktail = models.ForeignKey(Cocktail, on_delete=models.CASCADE)
    dose = models.IntegerField()
