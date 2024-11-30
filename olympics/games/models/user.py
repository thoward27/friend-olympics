from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

    from olympics.games.models.fixture import Fixture


class AvailableManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        queryset = super().get_queryset()
        return queryset.filter(
            models.Q(fixture__isnull=True) | models.Q(fixture__ended__isnull=False),
        )


class User(AbstractUser):
    """A user of the system."""

    score = models.PositiveIntegerField(default=settings.DEFAULT_SCORE)

    objects = UserManager()  # type: ignore[misc,assignment]
    available: "models.QuerySet[User]" = AvailableManager()  # type: ignore[assignment]

    fixture_set: "QuerySet[Fixture]"

    class Meta:
        ordering = ("username",)
