# person/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Person
from pprint import pprint
class PersonBaseTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = get_user_model().objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True,
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            phone='1234567890',
            date_of_birth='2000-01-01',
        )
        self.guest = get_user_model().objects.create_user(
            username='guest',
            password='guest123',
            is_staff=False,
            email='guest@example.com',
            first_name='Guest',
            last_name='User',
            phone='0987654321',
            date_of_birth='2001-09-01',
        )



class PersonViewSetTestCase(PersonBaseTestCase):
    def test_create_person(self):
        self.client.login(username='admin', password='admin123')
        data = {
            'username': 'test',
            'password': 'test123',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '1111111111',
            'dateOfBirth': '2002-01-01',
        }
        response = self.client.post('/person/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get('/person/', data, format='json')
        pprint(response.json())
        self.assertEqual(response.json()['count'], 3)

class FilterPersonViewSetTestCase(PersonBaseTestCase):
    def test_filtered_person_list(self):
        self.client.login(username='guest', password='guest123')
        response = self.client.get('/filter-person/?first_name=Ad&min_age=24&max_age=24', format='json')
        pprint(response.json())
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
