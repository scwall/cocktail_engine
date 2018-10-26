from django.db import models

# Create your models here.

class Bottle(models.Model):

    name = models.CharField(max_length=80)
    solenoidValve = models.IntegerField()
    step = models.IntegerField()
    empty = models.BooleanField(default=False)
    image = models.ImageField(upload_to='bottle_picture',null=True)
    def __str__(self):
        return self.name

class Cocktail(models.Model):

    name = models.CharField(max_length=80)
    description = models.TextField()
    bottles = models.ManyToManyField(Bottle, through='Bottles_belongs_cocktails', related_name='cocktails')
    image = models.ImageField(upload_to='cocktail_picture',null=True)
    def __str__(self):
        return self.name

class Bottles_belongs_cocktails(models.Model):

    bottle = models.ForeignKey(Bottle, on_delete=models.CASCADE)
    cocktail = models.ForeignKey(Cocktail, on_delete=models.CASCADE)
    dose = models.IntegerField()

    @property
    def Recipe_of_cocktails(self):
        return 'Bottle: {} | | Cocktail: {} | | Dose: {}'.format(self.bottle, self.cocktail, self.dose)
    def __str__(self):
        return str(self.dose)
