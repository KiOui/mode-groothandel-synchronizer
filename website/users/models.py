from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    """User manager object."""

    def _create_user(self, username, **kwargs):
        """
        Create user given a username.

        :param username: the username
        :param kwargs: optional extra fields
        :return: a new User object
        """
        user = self.model(username=username, **kwargs)
        if "password" in kwargs.keys():
            user.set_password(kwargs.pop("password"))
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, username, **kwargs):
        """
        Create a user given a username.

        :param username: the username
        :param kwargs: optional extra fields
        :return: a new User object
        """
        kwargs.setdefault("is_staff", False)
        kwargs.setdefault("is_superuser", False)
        return self._create_user(username, **kwargs)

    def create_superuser(self, username, **kwargs):
        """
        Create a superuser.

        :param username: the username
        :param kwargs: optional extra fields
        :return: a new User object
        """
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        return self._create_user(username, **kwargs)


class User(AbstractUser):
    """User object."""

    objects = UserManager()

    USERNAME_FIELD = "username"

    REQUIRED_FIELDS = ["email"]

    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=False)
    full_name = models.CharField(max_length=100)

    def __str__(self):
        """
        Convert user to string.

        :return: the username of the user
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.full_name:
            return self.full_name
        return self.username

    def get_short_name(self):
        """Get short name."""
        if self.first_name:
            return self.first_name
        elif self.full_name:
            return self.full_name
        else:
            return self.username
