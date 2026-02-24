from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom User model where email is the unique identifier for authentication
    instead of usernames.
    """
    username = None # Remove username field
    email = models.EmailField(_('email address'), unique=True)

    # Set email as the unique identifier for login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # Email is required by default; no other fields needed for createsuperuser

    def __str__(self):
        return self.email