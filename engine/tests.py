from django.test import TestCase

import signal

from bs4 import BeautifulSoup
from django.test import TestCase, Client, SimpleTestCase, LiveServerTestCase
from django.urls import reverse
from django.core.management import call_command
from django.test import TestCase
# Create your tests here.

from django.contrib.auth.models import User
from unittest import mock
import requests
import sys

from engine.models import Bottle, SolenoidValve, Cocktail, Bottles_belongs_cocktails


class CocktailEngineTest(LiveServerTestCase):
    def setUp(self):
        SolenoidValve.objects.create(id=1, number=1, step=10)
        SolenoidValve.objects.create(id=2, number=2, step=20)
        SolenoidValve.objects.create(id=3, number=3, step=30)
        SolenoidValve.objects.create(id=4, number=4, step=40)
        SolenoidValve.objects.create(id=5, number=5, step=50)
        SolenoidValve.objects.create(id=6, number=6, step=60)
        bottle_one = Bottle.objects.create(id=1, name='bottle1', solenoid_valve_id=1)
        bottle_two = Bottle.objects.create(id=2, name='bottle2', solenoid_valve_id=2)
        bottle_three = Bottle.objects.create(id=3, name='bottle3', solenoid_valve_id=3)
        bottle_four = Bottle.objects.create(id=4, name='bottle4', solenoid_valve_id=4)
        bottle_five = Bottle.objects.create(id=5, name='bottle5', solenoid_valve_id=5)
        bottle_six = Bottle.objects.create(id=6, name='bottle6', solenoid_valve_id=6)
        cocktail_one = Cocktail.objects.create(id=1, name="cocktailone", description='cocktail one description')
        cocktail_two = Cocktail.objects.create(id=2, name="cocktailtwo", description='cocktail two description')
        Bottles_belongs_cocktails(bottle=bottle_one, cocktail=cocktail_one,
                                  dose=1).save()
        Bottles_belongs_cocktails(bottle=bottle_two, cocktail=cocktail_two,
                                  dose=2).save()
        Bottles_belongs_cocktails(bottle=bottle_three, cocktail=cocktail_two,
                                  dose=3).save()

        self.client = Client()

    def test_solenoidValve(self):
        solenoid_valve = SolenoidValve.objects.get(number=1)
        self.assertEqual(solenoid_valve.step, 10)

    def test_bottle(self):
        bottle = Bottle.objects.get(name='bottle1')
        self.assertEqual(bottle.solenoid_valve_id, 1)

    def test_bottle_belong_cocktails(self):
        bottle = Bottles_belongs_cocktails.objects.get(bottle=1)
        self.assertEqual(bottle.bottle_id, 1)

    def test_cocktail(self):
        cocktail = Cocktail.objects.get(name="cocktailone")
        self.assertEqual(cocktail.description, 'cocktail one description')
        cocktail_by_bottle = Cocktail.objects.get(bottles_belongs_cocktails__bottle__name='bottle1')
        self.assertEqual(cocktail_by_bottle.description, 'cocktail one description')

    def test_cocktail_views(self):
        response = self.client.get(self.live_server_url + reverse('engine:cocktailViews'))

        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, features="html.parser")
        cocktail1 = soup.find_all(id="cocktailone")
        cocktail2 = soup.find_all(id="cocktailtwo")
        cocktail1 = cocktail1[0].find('p').text
        cocktail2 = cocktail2[0].find('p').text

        tags = soup.select('a[class="dropdown-item"]')
        self.assertEqual(cocktail1, 'Nom: cocktailone')
        self.assertEqual(cocktail2, 'Nom: cocktailtwo')
        self.assertListEqual([tag.text for tag in tags],
                             ['bottle1', 'bottle2', "bottle3", "bottle4", "bottle5", "bottle6"])

    def test_view_cocktail_views_name(self):
        response = self.client.get(self.live_server_url + reverse('engine:cocktailViews'), data={'name': 'cocktailone'})

        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, features="html.parser")
        tags = soup.select('a[class="dropdown-item"]')
        self.assertListEqual([tag.text for tag in tags],
                             ['bottle1', 'bottle2', "bottle3", "bottle4", "bottle5", "bottle6"])

    def test_view_cocktail_views_bottle(self):
        response = self.client.get(self.live_server_url + reverse('engine:cocktailViews'), data={'name': 'cocktailone'})

        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, features="html.parser")
        tags = soup.select('a[class="dropdown-item"]')
        self.assertListEqual([tag.text for tag in tags],
                             ['bottle1', 'bottle2', "bottle3", "bottle4", "bottle5", "bottle6"])
        cocktails = soup.find_all(id="cocktailone")
        cocktail = cocktails[0].find('p').text
        self.assertEqual(cocktail, 'Nom: cocktailone')
