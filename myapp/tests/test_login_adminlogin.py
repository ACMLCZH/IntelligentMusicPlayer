from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('sign_in_sign_up_reset_request') 
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_login_success(self):
        data = {
            'type': 'sign_in',
            'username': self.username,
            'password': self.password,
        }
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)  # check state code
        self.assertEqual(response.json()['response'], 'Log In Successful!')  # check response
        self.assertTrue(response.json()['redirect'])  # check redirect
        self.assertEqual(response.json()['redirect_url'], reverse('index'))  # check redirect URL

    def test_login_invalid_credentials(self):
        data = {
            'type': 'sign_in',
            'username': self.username,
            'password': 'wrongpassword',
        }
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)  # check state code
        self.assertEqual(response.json()['response'], 'Invalid Username or Password')  # check response

class SignUpTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('sign_in_sign_up_reset_request') 

    def test_sign_up_success(self):
        data = {
            'type': 'sign_up',
            'username': 'testuser',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
        }
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)   # check state code
        self.assertEqual(response.json()['response'], 'Sign Up Successful!')  # check response
        self.assertTrue(response.json()['redirect'])  # check redirect
        self.assertEqual(response.json()['redirect_url'], reverse('login'))  # check redirect URL

        # 检查用户是否已创建
        user_exists = User.objects.filter(username='testuser').exists()
        self.assertTrue(user_exists)

    def test_sign_up_password_mismatch(self):
        data = {
            'type': 'sign_up',
            'username': 'testuser',
            'password': 'testpassword',
            'confirm_password': 'wrongpassword',
        }
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200) # check state code
        self.assertEqual(response.json()['response'], 'Passwords are not the same!')  # check response

    def test_sign_up_username_exists(self):
        # 先创建一个用户
        User.objects.create_user(username='testuser', password='testpassword')

        data = {
            'type': 'sign_up',
            'username': 'testuser',
            'password': 'testpassword',
            'confirm_password': 'testpassword',
        }
        response = self.client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)  # check state code
        self.assertEqual(response.json()['response'], 'Username already exists!')  # check response

class AdminTestCase(TestCase):
    def setUp(self):
        self.admin_username = 'admin'
        self.admin_password = 'adminpassword'
        self.admin_user = User.objects.create_superuser(username=self.admin_username, password=self.admin_password)

    def test_admin_login(self):
        response = self.client.post(reverse('admin:login'), {'username': self.admin_username, 'password': self.admin_password})
        self.assertEqual(response.status_code, 302)  # check redirect
        self.assertTrue(response.wsgi_request.user.is_authenticated)  # check user authenticated

    def test_admin_access(self):
        self.client.login(username=self.admin_username, password=self.admin_password)
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)  # check to admin
