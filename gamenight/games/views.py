# Create your views here.
import logging

import iommi  # type: ignore[import]
import iommi.templates
from cryptography import fernet
from django import http
from django.conf import settings
from django.contrib import auth

from gamenight.games import forms, models, tables


def login(request: http.HttpRequest, username: str, encrypted_password: str) -> http.HttpResponse:
    """Login to the gamenight portal.

    This is an insane way to do this, but it allows users to login by scanning their QR code.
    """
    user = models.User.objects.get(username=username)
    password = fernet.Fernet(settings.FERNET_KEY).decrypt(encrypted_password.encode())
    if user.check_password(password.decode()):
        auth.login(request, user)
    else:
        logging.error("Failed to login user %s %s", username, password)
    return http.HttpResponseRedirect("/")


class UserPage(iommi.Page):
    users = tables.UserTable()


class GamesPage(iommi.Page):
    games = tables.GameTable()


class GamePage(iommi.Page):
    body = iommi.Fragment(template="games/game_detail.html")


class FixturePage(iommi.Page):
    ongoing = tables.FixtureTable(
        title="Ongoing",
        rows=models.Fixture.objects.filter(ended=None).order_by("-started"),
    )
    ended = tables.FixtureTable(
        title="Ended",
        rows=models.Fixture.objects.exclude(ended=None).order_by("-started"),
    )


class FixtureDetailPage(iommi.Page):
    body = iommi.Fragment(template="games/fixture_detail.html")


class FixtureCreatePage(iommi.Page):
    # form = iommi.Form.create(auto__model=models.Fixture, auto__include=["game", "users"])
    form = forms.FixtureCreateForm()


class FixtureUpdatePage(iommi.Page):
    form = forms.FixtureUpdateForm()
