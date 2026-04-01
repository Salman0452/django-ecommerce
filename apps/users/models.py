from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.core.models import CoreModel


class User(AbstractUser, CoreModel):
    """Custom user model."""
    email = models.EmailField(unique=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
