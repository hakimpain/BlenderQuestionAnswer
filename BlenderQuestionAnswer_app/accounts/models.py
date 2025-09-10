from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    username = models.CharField(max_length=50,unique=True)
    email = models.CharField(max_length=100,unique=True)

    def __str__(self):
        return self.username


