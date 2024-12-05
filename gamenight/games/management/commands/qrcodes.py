import pathlib

import qrcode  # type: ignore[import]
from django.conf import settings
from django.core.management import base

from gamenight.games import models


class Command(base.BaseCommand):
    def handle(self, *_, **__) -> None:
        for user in models.User.objects.all():
            url = user.get_qr_code()
            img = qrcode.make(url)
            pathlib.Path(settings.BASE_DIR / "qrcodes").mkdir(exist_ok=True)
            img.save(settings.BASE_DIR / "qrcodes" / f"{user.username}.png")
            self.stdout.write(self.style.SUCCESS(f"Created QR code for {user.username} ({url})"))
