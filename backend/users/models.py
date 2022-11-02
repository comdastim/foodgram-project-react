from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(max_length=100, unique=True,blank=False, null=False,
                                verbose_name='Никнейм')
    email = models.EmailField(max_length=100, unique=True,
                              verbose_name='Адрес электронной почты')
    first_name = models.CharField(max_length=50, blank=True, verbose_name='Имя пользователя')
    last_name = models.CharField(max_length=50, blank=True, verbose_name='Фамилия')


    class Meta:
        ordering = ['-id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username