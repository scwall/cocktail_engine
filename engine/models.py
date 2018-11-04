from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.
class SolenoidValve(models.Model):
    number = models.IntegerField(validators=[MinValueValidator(1),
                                    MaxValueValidator(6)])
    step = models.IntegerField()

class Bottle(models.Model):
    name = models.CharField(max_length=80)
    empty = models.BooleanField(default=False)
    image = models.ImageField(upload_to='bottle_picture',blank=True, null=True,)
    solenoid_valve = models.OneToOneField(SolenoidValve,on_delete=models.CASCADE)
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
    def bottle_detail(self):
        return '{}'.format(self.bottle)

    @property
    def cocktail_detail(self):
        return '{}'.format(self.cocktail)

    @property
    def dose_detail(self):
        return '{}'.format(self.dose)
    def __str__(self):
        return str(self.dose)


