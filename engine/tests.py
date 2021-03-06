#!/usr/bin/python3
import json
from unittest import TestCase
from unittest.mock import patch, MagicMock

from celery.exceptions import Retry
from django.test import Client, LiveServerTestCase
from django.urls import reverse
from requestium import Session

from engine.models import Bottle, SolenoidValve, Cocktail, BottlesBelongsCocktails
from engine.tasks import make_cocktail





class CocktailEngineTest(LiveServerTestCase):
    """
    Test the web part of the project in live server
    """
    def setUp(self):
        self.browser = Session(webdriver_path='/usr/lib/chromium-browser/chromedriver',
                               browser='chrome',
                               default_timeout=15,
                               webdriver_options={
                                   'arguments':
                                       ['--headless', '--no-sandbox', '--disable-dev-shm-usage']})
        SolenoidValve.objects.create(id=1, number=1, step=10, first_pin=1, second_pin=2)
        SolenoidValve.objects.create(id=2, number=2, step=20, first_pin=1, second_pin=2)
        SolenoidValve.objects.create(id=3, number=3, step=30, first_pin=1, second_pin=2)
        SolenoidValve.objects.create(id=4, number=4, step=40, first_pin=1, second_pin=2)
        SolenoidValve.objects.create(id=5, number=5, step=50, first_pin=1, second_pin=2)
        SolenoidValve.objects.create(id=6, number=6, step=60, first_pin=1, second_pin=2)
        bottle_one = Bottle.objects.create(id=1, name='bottle1', solenoid_valve_id=1)
        bottle_two = Bottle.objects.create(id=2, name='bottle2', solenoid_valve_id=2)
        bottle_three = Bottle.objects.create(id=3, name='bottle3', solenoid_valve_id=3)
        bottle_four = Bottle.objects.create(id=4, name='bottle4', solenoid_valve_id=4, empty=True)
        bottle_five = Bottle.objects.create(id=5, name='bottle5', solenoid_valve_id=5)
        Bottle.objects.create(id=6, name='bottle6', solenoid_valve_id=6)
        cocktail_one = Cocktail.objects.create \
            (id=1, name="cocktailone", description='cocktail one description')
        cocktail_two = Cocktail.objects.create \
            (id=2, name="cocktailtwo", description='cocktail two description')
        cocktail_three = Cocktail.objects.create \
            (id=3, name="cocktailthree", description='cocktail three description')
        BottlesBelongsCocktails(bottle=bottle_one, cocktail=cocktail_one,
                                dose=1).save()
        BottlesBelongsCocktails(bottle=bottle_two, cocktail=cocktail_two,
                                dose=2).save()
        BottlesBelongsCocktails(bottle=bottle_three, cocktail=cocktail_two,
                                dose=3).save()
        BottlesBelongsCocktails(bottle=bottle_four, cocktail=cocktail_three,
                                dose=4).save()
        BottlesBelongsCocktails(bottle=bottle_five, cocktail=cocktail_three,
                                dose=4).save()

        self.client = Client()

    def tearDown(self):
        """
        Close browser if is finish

        """
        self.browser.driver.close()
        self.browser.close()

    def test_solenoid_valve(self):
        """
        Test if the step this object is good equal
        """
        solenoid_valve = SolenoidValve.objects.get(number=1)
        self.assertEqual(solenoid_valve.step, 10)

    def test_bottle(self):
        """
        Test if __str__ correctly return the name of the object in the database
        """
        bottle = Bottle.objects.get(name='bottle1')
        self.assertEqual(bottle.solenoid_valve_id, 1)
        self.assertEqual(str(bottle), 'bottle1')

    def test_bottle_belong_cocktails(self):
        """
        Test if the many-to-many relationship is working properly
        """
        bottle = BottlesBelongsCocktails.objects.get(bottle=1)
        cocktail = BottlesBelongsCocktails.objects.get(cocktail=1)
        self.assertEqual(bottle.bottle_id, 1)
        self.assertEqual(bottle.bottle_detail, 'bottle1')
        self.assertEqual(cocktail.cocktail_detail, 'cocktailone')
        self.assertEqual(cocktail.dose_detail, '1')
        self.assertEqual(str(cocktail), '1')

    def test_cocktail(self):
        """
        Test if the cocktail exists and meets the requirements
        """
        cocktail = Cocktail.objects.get(name="cocktailone")
        self.assertEqual(cocktail.description, 'cocktail one description')
        self.assertEqual(str(cocktail), 'cocktailone')
        cocktail_by_bottle = Cocktail.objects.get(bottlesbelongscocktails__bottle__name='bottle1')
        self.assertEqual(cocktail_by_bottle.description, 'cocktail one description')

    def test_cocktail_views(self):
        """
        Test if the cocktails are well displayed on the page of the view,
        or if the bottles are well in the list
        """
        response = self.client.get(self.live_server_url +
                                   reverse('engine:cocktail_views'))
        self.assertEqual(response.status_code, 200)
        self.browser.driver.get(self.live_server_url +
                                reverse('engine:cocktail_views'))
        tags = self.browser.driver.find_elements_by_class_name('dropdown-item')
        cocktail1 = self.browser.driver.find_element_by_id \
            ('cocktailone').find_element_by_tag_name('p').get_attribute \
            ("innerText")
        cocktail2 = self.browser.driver.find_element_by_id \
            ('cocktailtwo').find_element_by_tag_name('p').get_attribute \
            ("innerText")
        self.assertEqual(cocktail1, 'Nom: cocktailone')
        self.assertEqual(cocktail2, 'Nom: cocktailtwo')
        self.assertListEqual([tag.get_attribute("text") for tag in tags],
                             ['bottle1', 'bottle2', "bottle3",
                              "bottle4", "bottle5", "bottle6"])

    def test_view_cocktail_views_research(self):
        """
        Test the cocktail view if a search was made from a name of a cocktail
        """
        self.browser.driver.get(self.live_server_url +
                                reverse('engine:cocktail_views') + "?name=cocktailone")

        cocktail = self.browser.driver.find_element_by_id \
            ('cocktailone').find_element_by_tag_name('p').get_attribute \
            ("innerText")
        self.assertEqual(cocktail, 'Nom: cocktailone')

    def test_view_cocktail_views_bottle(self):
        """
        Test the view of cocktails when a bottle has been selected
        """
        self.browser.driver.get(self.live_server_url +
                                reverse('engine:cocktail_views') + "?bottle=2")
        cocktail = self.browser.driver.find_element_by_id \
            ('cocktailtwo').find_element_by_tag_name('p').get_attribute \
            ("innerText")
        self.assertEqual(cocktail, 'Nom: cocktailtwo')

    @patch('engine.views.make_cocktail.delay', lambda x: 0)
    @patch('engine.views.make_cocktail.app.control.inspect', MagicMock())
    def test_view_make_cocktail(self):
        """
        Test the creation of a cocktail selected in a view
        """
        response = self.client.post(self.live_server_url +
                                    reverse('engine:make_the_cocktail'), {"cocktail_id": "1"},
                                    **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        response_json = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response_json['task_id'], 'error')

        response = self.client.post(self.live_server_url +
                                    reverse('engine:make_the_cocktail'),
                                    {"task_id": response_json['task_id']},
                                    **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        response_json = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['task_info'], 0)

        response = self.client.post(self.live_server_url +
                                    reverse('engine:make_the_cocktail'), {"cocktail_id": "3"},
                                    **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        response_json = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json['task_id'], 'error')

    def test_bottle_admin(self):
        """
        Test the addition of a bottle or the removal of it in the page "administration of bottles"
        """
        self.browser.driver.get(self.live_server_url +
                                reverse('engine:bottle_engine_admin'))
        bottle = self.browser.driver.find_element_by_id \
            ('bottle_6').find_element_by_tag_name('p').get_attribute \
            ("innerText")
        self.assertEqual(bottle, 'Nom: bottle6')
        response = self.client.get(self.live_server_url +
                                   reverse('engine:bottle_engine_admin') + '?deleteBottle=6')
        self.assertEqual(response.status_code, 302)

        self.client.post(self.live_server_url +
                         reverse('engine:bottle_engine_admin'),
                         {'solenoidValve': 6,
                          'name': 'bottle7', 'empty': 'False'})
        self.assertEqual(response.status_code, 302)
        self.browser.driver.get(self.live_server_url +
                                reverse('engine:bottle_engine_admin'))
        bottle = self.browser.driver.find_element_by_id \
            ('bottle_6').find_element_by_tag_name('p').get_attribute \
            ("innerText")
        self.assertEqual(bottle, 'Nom: bottle7')

    def test_bottle_admin_modify_bottle(self):
        """
        Test the modification of a bottle
        if it is empty or when it is not well synchronized under the valve
        """
        response = self.client.post(self.live_server_url +
                                    reverse('engine:bottle_modify_parameter'),
                                    {"step": 61, "solenoidValve": 6},
                                    **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)
        solenoid_valve = SolenoidValve.objects.get(id=6)
        self.assertEqual(solenoid_valve.step, 61)
        self.client.post(self.live_server_url +
                         reverse('engine:bottle_modify_parameter'),
                         {"empty": 'true', "solenoidValve": 6},
                         **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'})
        bottle = Bottle.objects.get(solenoid_valve__number=6)
        self.assertTrue(bottle.empty, True)

    def test_cocktail_admin_add_cocktail(self):
        """
        Test the addition of a cocktail in the page "administration of cocktails"
        """
        response = self.client.post(self.live_server_url +
                                    reverse('engine:cocktail_engine_admin'),
                                    {'name': 'cocktailfive',
                                     'description': 'cocktail five',
                                     'image': [''],
                                     'form-TOTAL_FORMS': ['1'],
                                     'form-MIN_NUM_FORMS': ['0'],
                                     'form-MAX_NUM_FORMS': ['6'],
                                     'form-INITIAL_FORMS': ['0'],
                                     'form-0-dose': ['2'],
                                     'form-0-bottle': ['bottle1'],
                                     'form-1-dose': ['3'],
                                     'form-1-bottle': ['bottle2'],
                                     })
        self.assertEqual(response.status_code, 200)
        self.browser.driver.get(self.live_server_url +
                                reverse('engine:cocktail_engine_admin'))
        cocktail1 = self.browser.driver.find_element_by_id \
            ('cocktailone').find_element_by_tag_name('p').get_attribute \
            ("innerText")
        cocktail2 = self.browser.driver.find_element_by_id \
            ('cocktailtwo').find_element_by_tag_name('p').get_attribute \
            ("innerText")
        cocktail5 = self.browser.driver.find_element_by_id \
            ('cocktailfive').find_element_by_tag_name('p').get_attribute \
            ("innerText")
        response = self.client.get(self.live_server_url +
                                   reverse('engine:cocktail_engine_admin') +
                                   '?deleteCocktail=3')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(cocktail1, "Nom: cocktailone")
        self.assertEqual(cocktail2, "Nom: cocktailtwo")
        self.assertEqual(cocktail5, 'Nom: cocktailfive')


class CeleryTaskEngineTest(TestCase):
    """
    Spot test create in celery, for the hardware part
    """
    @patch('engine.tasks.make_cocktail')
    @patch('engine.tasks.current_task', MagicMock(update_state=(MagicMock())))
    @patch('engine.tasks.MCP3008.read_adc', MagicMock(return_value=1))
    @patch('engine.tasks.GPIO.input', MagicMock(return_value=False))
    def test_my_task_is_called(self, mock_cocktail_task):
        """
        Test if the task does not return an error during its execution
        """
        mock_cocktail_task.side_effect = Retry()
        self.assertRaises(Retry, make_cocktail([{'step': 1,
                                                 'first_pin': 1,
                                                 'second_pin': 2,
                                                 'solenoidvalve': 3,
                                                 'dose': 1}]))
