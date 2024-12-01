import logging
from typing import TYPE_CHECKING

from asgiref import sync
from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from olympics.games import broadcaster

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

    from olympics.games.models.fixture import Fixture


class AvailableManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        queryset = super().get_queryset()
        return queryset.filter(
            models.Q(fixture__isnull=True) | models.Q(fixture__ended__isnull=False),
        ).distinct()


class User(AbstractUser):
    """A user of the system."""

    score = models.PositiveIntegerField(default=settings.DEFAULT_SCORE)

    objects = UserManager()  # type: ignore[misc,assignment]
    available: "models.QuerySet[User]" = AvailableManager()  # type: ignore[assignment]

    fixture_set: "QuerySet[Fixture]"

    class Meta:
        ordering = ("username",)

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        self.broadcast_score()

    def broadcast_score(self) -> None:
        try:
            sync.async_to_sync(UserBroadcaster().send_score)(self.username, self.score)
        except Exception:
            logging.exception("Failed to broadcast user score: %s %s", self.username, self.score)


class UserBroadcaster(broadcaster.BaseBroadcaster):
    async def send_score(self, username: str, score: int) -> None:
        await self.layer.group_send(
            username,
            {"type": "user.score", "score": score},
        )
