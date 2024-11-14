# final-project
 520 Final Project


usage:

# STEP0: (Not required)
```python
# if you have mysql client in your computer
# 取消注释myproject/settings.py 43~52行
# 注释这一行之后代表user account相关的database处理暂时被禁用

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 使用 MYSQL 数据库
        'NAME': 'project_user',  # 数据库名称
        'USER': 'root',  # 数据库用户名
        'PASSWORD': 'zyzjga1314',  # 数据库密码
        'HOST': 'localhost',  # 数据库地址
        'PORT': '3306',  # 数据库端口
    }
}

```

# STEP1: run backend server
```bash
python manage.py runserver
```

# STEP2: For Normal User, Open Login URL
```bash
# Open your browser with following link:
http://127.0.0.1:8000/login
# you will also see this url in your backend terminal
```

# STEP3: For Administator, Sign Up A Super Account(Administrator)
```bash
python manage.py createsuperuser
# enter your username, password, email

# A basic Administrator account that can be used (If you don't want to register another)
Username: 23687
Password: 520project
```

# STEP4: For Administator, Open Database Management URL
```bash
# Open your broser with following link:
http://127.0.0.1:8000/admin
# You may manage all accounts
```
