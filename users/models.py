from django.db import models
from django.core.validators import EmailValidator, RegexValidator

class Users(models.Model):
    name = models.CharField(max_length=25)
    email = models.EmailField(max_length=254, unique=True, validators=[
        EmailValidator(message="Enter a valid email address"),
        RegexValidator(
            regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            message='Enter a valid email address'
        )
    ])
    password = models.CharField(max_length=128)
    photo = models.ImageField(upload_to='photos/')
    role = models.CharField(max_length=20, choices=[
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('employer', 'Employer')
    ], default='student')

    def __str__(self):
        return self.name
