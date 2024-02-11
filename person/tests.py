from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status
from person.serializers import FilterPersonSerializer, PersonSerializer
from datetime import date
from pprint import pprint


user_model = get_user_model()

class TestCaseWithUsers(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = user_model.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True,
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            phone='1234567890',
            date_of_birth='2000-01-01',
        )
        self.guest_user = user_model.objects.create_user(
            username='guest',
            password='guest123',
            is_staff=False,
            email='guest@example.com',
            first_name='Guest',
            last_name='User',
            phone='0987654321',
            date_of_birth='2001-09-01',
        )


class AuthenticationTestCase(TestCaseWithUsers):
    def test_login_success(self):
        self.assertTrue(self.client.login(username='guest', password='guest123'))

    def test_login_no_such_user(self):
        self.assertFalse(self.client.login(username='adm', password='admin123'))

    def test_login_wrong_password(self):
        self.assertFalse(self.client.login(username='admin', password='admin1234'))

 
class PersonModelTestCase(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'date_of_birth': date(1990, 1, 1),
            'phone': '+1234567890'
        }

    def test_person_creation(self):
        user = user_model.objects.create(**self.user_data)
        self.assertIsInstance(user, user_model)
        self.assertEqual(user.username, 'testuser')

    def test_phone_regex_validator(self):
        # Test phone number validation
        # Valid phone number with +
        user = user_model.objects.create(**self.user_data)
        self.assertEqual(user.phone, '+1234567890')

        # Valid phone number without +
        user.phone = '1234567890'
        user.full_clean()

        # Invalid phone number (too short)
        with self.assertRaises(ValidationError):
            user.phone = '12345'
            user.full_clean()  # Run full_clean to trigger validation

        # Invalid phone number (too long)
        with self.assertRaises(ValidationError):
            user.phone = '+1234567890123456'
            user.full_clean()  

    def test_get_age(self):
        # Test the get_age method
        user = user_model.objects.create(**self.user_data)
        age = user.get_age()
        self.assertEqual(age, 34) # Birthday passed (01-01)
        
        user.date_of_birth = date(1990, 6, 1)
        age = user.get_age()
        self.assertEqual(age, 33) # Birthday not passed

    def test_age_calculation_with_no_birth_date(self):
        user = user_model.objects.create(**self.user_data)
        user.date_of_birth = None
        self.assertIsNone(user.get_age())


class SerializerTestCase(TestCaseWithUsers):
    def test_password_hashing(self):
        # Test password hashing in serializer
        serializer = PersonSerializer(data={'username': 'user', 'password': 'testpassword'})
        self.assertTrue(serializer.is_valid())
        self.assertTrue('password' in serializer.validated_data)
        self.assertNotEqual(serializer.validated_data['password'], 'testpassword')

    def test_person_serializer_fields(self):
        person_serializer = PersonSerializer()
        person_fields = person_serializer.fields.keys()
        self.assertTrue(all(field in person_fields for field in ['username', 'password', 'is_staff']))

    def test_filter_person_serializer_fields(self):
        filter_person_serializer = FilterPersonSerializer()
        filter_person_fields = filter_person_serializer.fields.keys()
        self.assertFalse(any(field in filter_person_fields for field in ['username', 'password', 'is_staff']))

class PersonViewSetTestCase(TestCaseWithUsers):
    # Test CRUD operations for the /person/ endpoint
    def test_create(self):
        # Test creating a new person object
        self.client.force_authenticate(user=self.admin_user)
        create_data = {
            'username': 'newuser',
            'password': 'newpassword',
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'jane@example.com',
            'date_of_birth': '1990-01-01',
            'phone': '+1234567890'
        }
        create_url = reverse('person-list')
        response = self.client.post(create_url, create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        num_users = user_model.objects.all()
        self.assertEqual(len(num_users), 3)

    def test_list(self):
        # Test retrieving a list of person objects
        self.client.force_authenticate(user=self.admin_user)
        list_url = reverse('person-list')
        response = self.client.get(list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_update(self):
        # Test update a person object
        self.client.force_authenticate(user=self.admin_user)
        update_url = reverse('person-detail', args=[self.admin_user.pk])
        pprint(update_url) 
        update_data = {'first_name': 'Jane'}
        response = self.client.patch(update_url, update_data, format='json')
        pprint(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        admin = user_model.objects.get(username='admin')
        admin.refresh_from_db()
        self.assertEqual(admin.first_name, 'Jane')

    def test_delete_person(self):
        # Test deleting a person object
        self.assertEqual(user_model.objects.count(), 2)
        self.client.force_authenticate(user=self.admin_user)
        delete_url = reverse('person-detail', args=[self.guest_user.pk])
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(user_model.objects.count(), 1)


    def test_regular_user_access(self):
        # Test that regular users can't perform CRUD operations
        self.client.force_authenticate(user=self.guest_user)

        # Create
        create_url = reverse('person-list')
        create_data = {'username': 'newuser', 'password': 'newpassword', 'first_name': 'Jane', 'last_name': 'Doe'}
        self.assertEqual(user_model.objects.count(), 2)
        response = self.client.post(create_url, create_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(user_model.objects.count(), 2)

        # Retrieve
        person = user_model.objects.create(username='testuser', password='testpassword', first_name='John', last_name='Doe')
        retrieve_url = reverse('person-detail', args=[person.pk])
        response = self.client.get(retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Update
        update_url = reverse('person-detail', args=[person.pk])
        update_data = {'first_name': 'Jane'}
        response = self.client.patch(update_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        person.refresh_from_db()
        self.assertEqual(person.first_name, 'John')

        # Delete
        delete_url = reverse('person-detail', args=[person.pk])
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(user_model.objects.count(), 3)


class FilterPersonViewSetTestCase(TestCaseWithUsers):
    def test_filter_person_endpoint(self):
        self.client.force_authenticate(user=self.guest_user)
        response = self.client.get(reverse('filter-person-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 2)

    def test_filter_person_by_first_name(self):
        # Test filtering persons by first name
        person1 = user_model.objects.create(username='user1', first_name='John', last_name='Doe', date_of_birth=date(1990, 1, 1))
        person2 = user_model.objects.create(username='user2', first_name='Jane', last_name='Doe', date_of_birth=date(1990, 1, 1))
        self.client.force_authenticate(user=self.guest_user)
        response = self.client.get(reverse('filter-person-list'), {'first_name': 'John'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['first_name'], 'John')

    def test_filter_person_by_last_name(self):
        # Test filtering persons by last name
        person1 = user_model.objects.create(username='user1', first_name='John', last_name='Doe', date_of_birth=date(1990, 1, 1))
        person2 = user_model.objects.create(username='user2', first_name='Jane', last_name='Smith', date_of_birth=date(1990, 1, 1))
        self.client.force_authenticate(user=self.guest_user)
        response = self.client.get(reverse('filter-person-list'), {'last_name': 'Doe'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['last_name'], 'Doe')

    def test_filter_person_no_results(self):
        # Test filtering with no results
        self.client.force_authenticate(user=self.guest_user)
        response = self.client.get(reverse('filter-person-list'), {'first_name': 'NonExistent'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 0)

    def test_filter_person_partial_first_name(self):
        # Test filtering with partial first name
        person1 = user_model.objects.create(username='user1', first_name='John', last_name='Doe', date_of_birth=date(1990, 1, 1))
        person2 = user_model.objects.create(username='user2', first_name='Jane', last_name='Doe', date_of_birth=date(1990, 1, 1))
        self.client.force_authenticate(user=self.guest_user)
        response = self.client.get(reverse('filter-person-list'), {'first_name': 'Jo'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['first_name'], 'John')

    def test_filter_person_by_age_range(self):
        # Test filtering persons by age range
        person1 = user_model.objects.create(username='user1', first_name='John', last_name='Doe', date_of_birth=date(1990, 1, 1))
        person2 = user_model.objects.create(username='user2', first_name='Jane', last_name='Doe', date_of_birth=date(2000, 1, 1))
        self.client.force_authenticate(user=self.guest_user)
        response = self.client.get(reverse('filter-person-list'), {'min_age': '30', 'max_age': '40'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['first_name'], 'John')

    def test_filter_person_invalid_age(self):
        # Test filtering with invalid age parameter
        self.client.force_authenticate(user=self.guest_user)
        response = self.client.get(reverse('filter-person-list'), {'min_age': 'abc', 'max_age': '50'})
        pprint(response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('min_age', response.json())

        response = self.client.get(reverse('filter-person-list'), {'min_age': '40', 'max_age': 'xyz'})
        pprint(response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('max_age', response.json())

    def test_filter_person_with_name_and_age(self):
        self.client.force_authenticate(user=self.guest_user)
        response = self.client.get(reverse('filter-person-list'), {'first_name': 'ad', 'max_age':'25'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['results']), 1)


    def test_filter_person_with_large_user_numbers(self):
        for i in range(1000):
            user_model.objects.create(username=f'user{i:03d}', password='password', first_name=f'John{i:03d}', last_name='Doe')
        self.client.force_authenticate(user=self.guest_user)
        response = self.client.get(reverse('filter-person-list'), {'first_name': 'John00'})
        self.assertEqual(response.json()['count'], 10)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ErrorHandlingTestCase(TestCaseWithUsers):
    def test_invalid_input(self):
        self.client.force_authenticate(user=self.admin_user)
        invalid_data = {'username': '', 'password': 'testpassword'}
        response = self.client.post(reverse('person-list'), data=invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_duplicate_username(self):
        self.client.force_authenticate(user=self.admin_user)
        create_data = {
            'username': 'guest',
            'password': 'guestpassword',
        }
        response = self.client.post(reverse('person-list'), data=create_data, format='json')
        pprint(response.json())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('A user with that username already exists.', response.json()['username'])


class PaginationTestCase(TestCaseWithUsers):
    def test_pagination(self):
        user_model.objects.create(username='user', password='password', first_name='John', last_name='Doe')
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse('person-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pprint(response.json())
        self.assertEqual(response.json()['count'], 3)
        self.assertIn('?page=2', response.json()['next'])
