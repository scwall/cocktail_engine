from django.test import TestCase

import signal

from bs4 import BeautifulSoup
from django.test import TestCase, Client, SimpleTestCase, LiveServerTestCase
from django.urls import reverse
from django.core.management import call_command
from django.test import TestCase
from selenium import webdriver
# Create your tests here.

from django.contrib.auth.models import User
from unittest import mock
import requests
import sys
from selenium import webdriver
from requestium import Session, Keys
from engine.models import Bottle, SolenoidValve, Cocktail, Bottles_belongs_cocktails


class CocktailEngineTest(LiveServerTestCase):
    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('--no-sandbox')
        # self.browser = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', chrome_options=options)
        self.browser = Session(webdriver_path='/usr/lib/chromium-browser/chromedriver',
                               browser='chrome',
                               default_timeout=15,
                               webdriver_options={'arguments': ['headless']})
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
        self.assertEqual(str(bottle), 'bottle1')

    def test_bottle_belong_cocktails(self):
        bottle = Bottles_belongs_cocktails.objects.get(bottle=1)
        cocktail = Bottles_belongs_cocktails.objects.get(cocktail=1)
        self.assertEqual(bottle.bottle_id, 1)
        self.assertEqual(bottle.bottle_detail, 'bottle1')
        self.assertEqual(cocktail.cocktail_detail, 'cocktailone')
        self.assertEqual(cocktail.dose, 1)

    def test_cocktail(self):
        cocktail = Cocktail.objects.get(name="cocktailone")
        self.assertEqual(cocktail.description, 'cocktail one description')
        self.assertEqual(str(cocktail), 'cocktailone')
        cocktail_by_bottle = Cocktail.objects.get(bottles_belongs_cocktails__bottle__name='bottle1')
        self.assertEqual(cocktail_by_bottle.description, 'cocktail one description')

    def test_cocktail_views(self):
        response = self.client.get(self.live_server_url + reverse('engine:cocktailViews'))
        self.assertEqual(response.status_code, 200)
        self.browser.driver.get(self.live_server_url + reverse('engine:cocktailViews'))
        tags = self.browser.driver.find_elements_by_class_name('dropdown-item')
        cocktail1 = self.browser.driver.find_element_by_id('cocktailone').find_element_by_tag_name('p').get_attribute(
            "innerText")
        cocktail2 = self.browser.driver.find_element_by_id('cocktailtwo').find_element_by_tag_name('p').get_attribute(
            "innerText")
        self.assertEqual(cocktail1, 'Nom: cocktailone')
        self.assertEqual(cocktail2, 'Nom: cocktailtwo')
        self.assertListEqual([tag.get_attribute("text") for tag in tags],
                             ['bottle1', 'bottle2', "bottle3", "bottle4", "bottle5", "bottle6"])

    def test_view_cocktail_views_research(self):
        self.browser.driver.get(self.live_server_url + reverse('engine:cocktailViews') + "?name=cocktailone")

        cocktail = self.browser.driver.find_element_by_id('cocktailone').find_element_by_tag_name('p').get_attribute(
            "innerText")
        self.assertEqual(cocktail, 'Nom: cocktailone')

    def test_view_cocktail_views_bottle(self):
        self.browser.driver.get(self.live_server_url + reverse('engine:cocktailViews') + "?bottle=2")
        cocktail = self.browser.driver.find_element_by_id('cocktailtwo').find_element_by_tag_name('p').get_attribute(
            "innerText")
        self.assertEqual(cocktail, 'Nom: cocktailtwo')

    def test_admin_bottle(self):
        response = self.client.post(self.live_server_url + reverse('engine:makeCocktail'), {"cocktail_id": "1"},
                                    **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)
