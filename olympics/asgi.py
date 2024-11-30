"""ASGI config for olympics project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from channels import (  # type: ignore[import]
    auth,
    routing,
)
from channels.security import websocket  # type: ignore[import]
from django.core.asgi import get_asgi_application

from olympics.games import urls

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "olympics.settings")

django_asgi_app = get_asgi_application()

application = routing.ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": websocket.AllowedHostsOriginValidator(
            auth.AuthMiddlewareStack(routing.URLRouter(urls.websocket_urlpatterns)),
        ),
    },
)
