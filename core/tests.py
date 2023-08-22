import json
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from oauth2_provider.models import AccessToken
from .views import create_access_token

class SignInViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_valid_credentials(self):
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(reverse('signin'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn('access_token', response_data)

    def test_invalid_credentials(self):
        data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post(reverse('signin'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, {'error': 'User did not authenticate'})

    def test_missing_username(self):
        data = {'password': 'testpassword'}
        response = self.client.post(reverse('signin'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, {'error': 'Invalid JSON data'})

    def test_missing_password(self):
        data = {'username': 'testuser'}
        response = self.client.post(reverse('signin'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, {'error': 'Invalid JSON data'})

    def test_hash_is_not_accepted_as_a_password(self):
        response = self.client.post(reverse('signin'), {'username': 'testuser', 'password': self.user.password}, content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_inactive_user_cannot_sign_in(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(reverse('signin'), {'username': 'testuser', 'password': 'testpassword'}, content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_non_object_and_malformed_json(self):
        for body in ['[]', 'null', '{', '{"username": 42, "password": "value"}']:
            with self.subTest(body=body):
                response = self.client.post(reverse('signin'), body, content_type='application/json')
                self.assertEqual(response.status_code, 400)

    def test_access_token_authenticates_greeting(self):
        token = create_access_token(self.user)
        response = self.client.post('/greeting', {'greeting': 'Hello'}, content_type='application/json', HTTP_AUTHORIZATION='Bearer ' + token.token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'message': 'Goodbye!'})

    def test_greeting_requires_token(self):
        response = self.client.post('/greeting', {'greeting': 'Hello'}, content_type='application/json')
        self.assertEqual(response.status_code, 403)
