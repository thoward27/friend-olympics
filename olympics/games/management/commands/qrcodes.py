from django.core.management import base
from olympics.games import models
import qrcode
import hashlib
from django.conf import settings
import pathlib

class Command(base.BaseCommand):
    def handle(self, *args, **options):
        for user in models.User.objects.all():
            default_password = hashlib.sha256(f"{user.first_name}{user.last_name}".encode()).hexdigest()
            img = qrcode.make(f"{settings.HOST}/auth/login/{user.username}/{default_password}")
            pathlib.Path(settings.BASE_DIR / "qrcodes").mkdir(exist_ok=True)
            img.save(settings.BASE_DIR / "qrcodes" / f"{user.username}.png")
            self.stdout.write(self.style.SUCCESS(f"Created QR code for {user.username}"))
