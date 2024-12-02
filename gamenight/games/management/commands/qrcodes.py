import hashlib
import pathlib

import qrcode  # type: ignore[import]
from cryptography import fernet
from django.conf import settings
from django.core.management import base

from gamenight.games import models


class Command(base.BaseCommand):
    def handle(self, *_, **__) -> None:
        for user in models.User.objects.all():
            default_password = hashlib.sha256(
                f"{user.first_name}{user.last_name}".encode(),
            ).hexdigest()
            encrypted_password = (
                fernet.Fernet(settings.FERNET_KEY).encrypt(default_password.encode()).decode()
            )
            url = f"{settings.SCHEMA}://{settings.HOST}/auth/login/{user.username}/{encrypted_password}"
            img = qrcode.make(url)
            pathlib.Path(settings.BASE_DIR / "qrcodes").mkdir(exist_ok=True)
            img.save(settings.BASE_DIR / "qrcodes" / f"{user.username}.png")
            self.stdout.write(self.style.SUCCESS(f"Created QR code for {user.username} ({url})"))
