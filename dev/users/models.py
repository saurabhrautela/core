"""Models to interact with the database."""
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.conf import settings


class UserProfileManager(BaseUserManager):
    """Manager for user profiles."""

    def create_user(self, email, username, password=None):
        """Create a new user profile."""
        if not email:
            raise ValueError("User must have an email address.")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username)

        if len(password) > settings.MAX_PASSWORD_LENGTH:
            truncated_password = password[: settings.MAX_PASSWORD_LENGTH]
        else:
            truncated_password = password

        user.set_password(truncated_password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, username, password):
        """Create and save a new super user with given details."""
        user = self.create_user(email=email, username=username, password=password)

        user.is_superuser = True
        user.is_staff = True
        user.roles = "UA"

        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Information for authentication and authorization."""

    states = (
        ("I", "Initialized"),
        ("L", "Locked"),
        ("A", "Activated"),
        ("D", "Deactivated"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(db_index=True, max_length=255, unique=True)
    username = models.CharField(db_index=True, max_length=255, unique=True)
    roles = models.CharField(max_length=2, default="U")
    state = models.CharField(max_length=1, choices=states, default="A")
    default_password_flag = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserProfileManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        """Return string representation of the user."""
        return self.username
