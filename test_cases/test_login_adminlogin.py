from django.test import TestCase
from django.contrib.auth.models import User
import django 
django.setup()
from django.urls import reverse

# import os 
# os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject.settings'
# class LoginTestCase(TestCase):
#     def setUp(self):
#         self.username = 'testuser'
#         self.password = 'testpassword'
        
#     def test_sign_up(self):
        

    # def test_login(self):
    #     response = self.client.post(reverse('login'), {'username': self.username, 'password': self.password})
    #     self.assertEqual(response.status_code, 302)  # 检查是否重定向
    #     self.assertTrue(response.wsgi_request.user.is_authenticated)  # 检查用户是否已认证

    # def test_login_invalid(self):
    #     response = self.client.post(reverse('login'), {'username': self.username, 'password': 'wrongpassword'})
    #     self.assertEqual(response.status_code, 200)  # 登录页面应重新加载
    #     self.assertFalse(response.wsgi_request.user.is_authenticated)  # 用户不应被认证

class AdminTestCase(TestCase):
    def setUp(self):
        self.admin_username = 'admin'
        self.admin_password = 'adminpassword'
        self.admin_user = User.objects.create_superuser(username=self.admin_username, password=self.admin_password)

    def test_admin_login(self):
        response = self.client.post(reverse('admin:login'), {'username': self.admin_username, 'password': self.admin_password})
        self.assertEqual(response.status_code, 302)  # 检查是否重定向
        self.assertTrue(response.wsgi_request.user.is_authenticated)  # 检查用户是否已认证

    def test_admin_access(self):
        self.client.login(username=self.admin_username, password=self.admin_password)
        response = self.client.get(reverse('admin:index'))
        self.assertEqual(response.status_code, 200)  # 检查是否成功访问Admin页面

# if __name__ == '__main__':
#     login_test_case = LoginTestCase()
#     admin_test_case = AdminTestCase()
#     login_test_case.test_login()
#     admin_test_case.test_admin_login()