from django import test
from model_bakery import baker

from gamenight.games.models import Fixture, Game, User


class ModelsMixin:
    def make_user(self, **kwargs) -> User:
        return baker.make("games.User", **kwargs)

    def make_game(self, **kwargs) -> Game:
        return baker.make("Game", **kwargs)

    def make_fixture(self, *, users: list[User] | None = None, **kwargs) -> Fixture:
        fixture = baker.make("Fixture", **kwargs)
        if users:
            fixture.users.set(users)
        return fixture


class BaseTestCase(test.TestCase, ModelsMixin):
    pass
