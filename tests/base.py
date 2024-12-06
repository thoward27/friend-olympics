import json
import logging
import random

from django import test
from django.conf import settings
from model_bakery import baker

from gamenight.games import models


class ModelsMixin:
    def make_user(self, **kwargs) -> models.User:
        return baker.make("games.User", **kwargs)

    def make_game(self, **kwargs) -> models.Game:
        return baker.make("games.Game", **kwargs)

    def load_game_fixtures(self) -> list[models.Game]:
        with (settings.BASE_DIR / "fixtures" / "games.json").open() as f:
            games = json.load(f)
        for game in games:
            self.make_game(**game["fields"])
        return list(models.Game.objects.all())

    @staticmethod
    def rank_expected_score(rank: models.Rank) -> float:
        """Compute an expected score for a given rank."""
        mean = rank.user.score
        stdev = max(100 * (1 + rank.fixture.game.randomness / 3) - (mean / 10), 0)
        return random.normalvariate(mean, stdev)

    def make_fixture(
        self,
        *,
        users: list[models.User] | None = None,
        rank_users: bool = False,
        **kwargs,
    ) -> models.Fixture:
        fixture = baker.make("Fixture", **kwargs)
        if users:
            if len(users) < fixture.game.minimum_players:
                raise ValueError("Not enough users for the fixture.")
            if (max_players := fixture.game.maximum_players) is not None:
                users = users[:max_players]
            fixture.users.set(users)
            if rank_users:
                players = [(self.rank_expected_score(r), r) for r in fixture.rank_set.all()]
                players = sorted(players, key=lambda p: p[0], reverse=True)
                if fixture.game.ranked:
                    for i, (score, rank) in enumerate(players):
                        logging.debug("Ranked: score=%s,rank=%s", score, rank)
                        fixture.rank_set.filter(pk=rank.pk).update(rank=i + 1)
                else:
                    logging.debug("Win/Loss: score=%s,rank=%s", players[0][0], players[0][1])
                    fixture.rank_set.filter(pk=players[0][1].pk).update(rank=1)
                    fixture.rank_set.exclude(pk=players[0][1].pk).update(rank=2)
        return fixture


class BaseTestCase(test.TestCase, ModelsMixin):
    pass
