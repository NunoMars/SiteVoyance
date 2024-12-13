from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    Group,
    PermissionsMixin,
    Permission,
)

from django.utils.timezone import now
from clairvoyance.models import MajorArcana


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with teh given email and password.

        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",  # Ajoutez ou modifiez le related_name
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_set",  # Ajoutez ou modifiez le related_name
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )
    first_name = models.CharField(max_length=254, blank=True)
    second_name = models.CharField(max_length=254, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    email = models.EmailField(blank=False, unique=True)
    send_email = models.BooleanField(default=False)

    USERNAME_FIELD = "email"

    objects = CustomUserManager()

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def get_full_name(self):
        full_name = f"{self.first_name} {self.second_name}"
        return full_name.strip()

    def __str__(self):
        return self.email


class History(models.Model):
    """Class to define the History table."""

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created = models.DateTimeField(default=now)
    sorted_card = models.ForeignKey(MajorArcana, on_delete=models.CASCADE)
    chosed_theme = models.CharField(default="theme", max_length=20)

    class Meta:
        db_table = "history"


class DailySortedCards(models.Model):
    """
    rec the daily_cards
    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    sorted_cards_date = models.DateTimeField(default=now)
    daily_sorted_cards = models.ForeignKey(
        MajorArcana,
        verbose_name="Carte de la journée",
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "daily_cards"
