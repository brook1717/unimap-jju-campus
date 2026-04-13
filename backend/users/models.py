from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model substituting Django's built-in User.
    Extends AbstractUser so all standard fields (username, first_name,
    last_name, is_staff, etc.) are inherited; email is enforced unique
    to support future email-based or OAuth authentication.
    """

    email = models.EmailField(unique=True)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.username
