import random
import statistics

from gamenight.games import models
from tests import base


class TestSimulations(base.BaseTestCase):
    def build_fixtures(
        self,
        games: list[models.Game],
        users: list[models.User],
    ) -> list[models.Fixture]:
        random.shuffle(games)
        random.shuffle(users)
        fixtures = []
        for game in games:
            if len(users) >= game.minimum_players:
                max_players = min(game.maximum_players or len(users), 4)
                fixture = self.make_fixture(game=game, users=users[:max_players], rank_users=True)
                fixtures.append(fixture)
                users = users[max_players:]
        return fixtures

    def compute_error(self, true_scores: dict[str, int]) -> float:
        users = models.User.objects.all()
        deltas = [abs(true_scores[u.username] - u.score) for u in users]
        return statistics.stdev(deltas) / statistics.mean(true_scores.values())

    def test_25_player_party(self):
        users = [self.make_user() for _ in range(25)]
        true_scores = {user.username: round(random.normalvariate(1000, 500)) for user in users}
        errors = [self.compute_error(true_scores)]
        games = self.load_game_fixtures()
        for _ in range(20):
            fixtures = self.build_fixtures(games.copy(), users.copy())
            for fixture in fixtures:
                fixture.finish()
        errors.append(self.compute_error(true_scores))
        self.assertLessEqual(errors[0], errors[-1])
