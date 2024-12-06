import json
import random
import statistics

from django.conf import settings

from gamenight.games import models
from tests import base


class TestSimulations(base.BaseTestCase):
    def add_games(self) -> list[models.Game]:
        with (settings.BASE_DIR / "fixtures" / "games.json").open() as f:
            games = json.load(f)
        for game in games:
            self.make_game(**game["fields"])
        return list(models.Game.objects.all())

    def build_fixtures(
        self,
        players: list[models.User],
        games: list[models.Game],
    ) -> list[models.Fixture]:
        random.shuffle(players)
        random.shuffle(games)
        fixtures = []
        for game in games:
            if len(players) >= game.minimum_players:
                num_players = min(game.maximum_players or len(players), 4)
                fixture = self.make_fixture(game=game, users=players[:num_players])
                fixture.save()
                fixtures.append(fixture)
                players = players[num_players:]
        return fixtures

    def test_25_player_party(self):
        all_players = {user.username: (user, 0) for user in [self.make_user() for _ in range(25)]}
        for username, (user, _) in all_players.items():
            all_players[username] = (user, round(random.normalvariate(1000, 200)))
        all_games = self.add_games()
        for _ in range(50):
            players, _ = zip(*all_players.values(), strict=True)
            fixtures = self.build_fixtures(list(players).copy(), all_games.copy())
            for fixture in fixtures:
                players = fixture.users.all()
                for player in players:
                    mean = all_players[player.username][1]
                    stdev = 200 * (1 + fixture.game.randomness) - (mean / 20)
                    player.real_score = random.normalvariate(mean, stdev)
                players = sorted(players, key=lambda p: p.real_score, reverse=True)
                if fixture.game.ranked:
                    for i, player in enumerate(players):
                        models.Rank.objects.filter(user=player, fixture=fixture).update(rank=i + 1)
                else:
                    models.Rank.objects.filter(user=players[0], fixture=fixture).update(rank=1)
                    for player in players[1:]:
                        models.Rank.objects.filter(user=player, fixture=fixture).update(rank=2)
                fixture.finish()
        true_score_players = [
            (score, user.username[:10]) for _, (user, score) in all_players.items()
        ]
        final_score_players = [
            (user.score, user.username[:10]) for user in models.User.objects.all()
        ]
        true_score_players.sort(reverse=True, key=lambda x: x[1])
        final_score_players.sort(reverse=True, key=lambda x: x[1])
        scores = [
            (t[1], t[0], f[0], abs(t[0] - f[0]))
            for t, f in zip(true_score_players, final_score_players, strict=True)
        ]
        deltas = [d for _, _, _, d in scores]
        elos = [t for _, t, _, _ in scores]
        self.assertLessEqual(statistics.stdev(deltas) / statistics.mean(elos), 0.1)
