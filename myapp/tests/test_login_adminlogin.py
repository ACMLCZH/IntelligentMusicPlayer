
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

import json

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_sign_up_view(self):
        response = self.client.get(reverse('sign_up'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')

    def test_reset_password_view(self):
        response = self.client.get(reverse('reset_password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reset_password.html')

    def test_backend_login_process_sign_in_success(self):
        data = {
            'type': 'sign_in',
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(reverse('sign_in_sign_up_reset_request'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'response': 'Log In Successful!',
            'redirect': True,
            'redirect_url': reverse('index')
        })

    def test_backend_login_process_sign_in_failure(self):
        data = {
            'type': 'sign_in',
            'username': 'wronguser',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('sign_in_sign_up_reset_request'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'response': 'Invalid Username or Password'})

    def test_backend_login_process_sign_up_success(self):
        data = {
            'type': 'sign_up',
            'username': 'newuser',
            'password': 'newpassword',
            'confirm_password': 'newpassword'
        }
        response = self.client.post(reverse('sign_in_sign_up_reset_request'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'response': 'Sign Up Successful!',
            'redirect': True,
            'redirect_url': reverse('login')
        })

    def test_backend_login_process_sign_up_password_mismatch(self):
        data = {
            'type': 'sign_up',
            'username': 'newuser',
            'password': 'newpassword',
            'confirm_password': 'wrongpassword'
        }
        response = self.client.post(reverse('sign_in_sign_up_reset_request'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'response': 'Passwords are not the same!'})

    def test_backend_login_process_sign_up_username_exists(self):
        data = {
            'type': 'sign_up',
            'username': 'testuser',
            'password': 'newpassword',
            'confirm_password': 'newpassword'
        }
        response = self.client.post(reverse('sign_in_sign_up_reset_request'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'response': 'Username already exists!'})

    def test_backend_login_process_reset_success(self):
        data = {
            'type': 'reset',
            'username': 'testuser',
            'password': 'newpassword',
            'confirm_password': 'newpassword',
            'security_code': '0000'
        }
        response = self.client.post(reverse('sign_in_sign_up_reset_request'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'response': 'Reset Successful!',
            'redirect': True,
            'redirect_url': reverse('login')
        })

    def test_backend_login_process_reset_username_not_exists(self):
        data = {
            'type': 'reset',
            'username': 'nonexistentuser',
            'password': 'newpassword',
            'confirm_password': 'newpassword',
            'security_code': '0000'
        }
        response = self.client.post(reverse('sign_in_sign_up_reset_request'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'response': 'Username not exists!'})

    def test_backend_login_process_reset_wrong_security_code(self):
        data = {
            'type': 'reset',
            'username': 'testuser',
            'password': 'newpassword',
            'confirm_password': 'newpassword',
            'security_code': 'wrongcode'
        }
        response = self.client.post(reverse('sign_in_sign_up_reset_request'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'response': 'Wrong security code!!! Please ask administrator!!!'})

    def test_backend_login_process_reset_password_mismatch(self):
        data = {
            'type': 'reset',
            'username': 'testuser',
            'password': 'newpassword',
            'confirm_password': 'wrongpassword',
            'security_code': '0000'
        }
        response = self.client.post(reverse('sign_in_sign_up_reset_request'), data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'response': 'Passwords are not the same!'})

    def test_backend_login_process_invalid_json(self):
        response = self.client.post(reverse('sign_in_sign_up_reset_request'), data='invalid json', content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Invalid JSON'})

    def test_backend_login_process_invalid_request(self):
        response = self.client.get(reverse('sign_in_sign_up_reset_request'))
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Invalid request'})
