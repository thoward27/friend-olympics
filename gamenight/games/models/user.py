import base64
import io
import logging
from typing import TYPE_CHECKING

import qrcode
from asgiref import sync
from cryptography import fernet
from django import urls
from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from gamenight.games import broadcaster

if TYPE_CHECKING:
    from django.db.models.query import QuerySet
    from qrcode.image.pil import PilImage

    from gamenight.games.models.fixture import Fixture


class AvailableManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        queryset = super().get_queryset()
        # Exclude users that are in a fixture that has not ended.
        return queryset.exclude(
            models.Q(fixture__isnull=False) & models.Q(fixture__ended__isnull=True),
        )


class User(AbstractUser):
    """A user of the system."""

    DEFAULT_SCORE = 1000

    score = models.PositiveIntegerField(default=DEFAULT_SCORE)
    qrcode = models.URLField(null=False, blank=True, default="")

    objects = UserManager()  # type: ignore[misc,assignment]
    available: "models.QuerySet[User]" = AvailableManager()  # type: ignore[assignment]

    fixture_set: "QuerySet[Fixture]"

    class Meta:
        ordering = ("username",)

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        self.broadcast_score()

    def set_password(self, raw_password: str | None) -> None:
        super().set_password(raw_password)
        assert raw_password is not None
        self.set_qrcode(raw_password)

    def broadcast_score(self) -> None:
        try:
            sync.async_to_sync(UserBroadcaster().send_score)(self.username, self.score)
        except Exception:
            logging.exception("Failed to broadcast user score: %s %s", self.username, self.score)

    def set_qrcode(self, password: str) -> None:
        """Set the QR code for the user."""
        password = fernet.Fernet(settings.FERNET_KEY).encrypt(password.encode()).decode()
        self.qrcode = urls.reverse(
            "users:qr",
            kwargs={"username": self.username, "encrypted_password": password},
        )

    def get_qrcode(self) -> str:
        """Get the QR code for the user and return as a b64 string."""
        url = f"{settings.SCHEMA}://{settings.HOST}{self.qrcode}"
        img: PilImage = qrcode.make(url)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()


class UserBroadcaster(broadcaster.BaseBroadcaster):
    async def send_score(self, username: str, score: int) -> None:
        await self.layer.group_send(
            username[:99],
            {"type": "user.score", "score": score},
        )
