import datetime

from django.db import IntegrityError

from tests import base


class TestFixture(base.BaseTestCase):
    def test_elo_updates__win_lose(self):
        game = self.make_game(ranked=False)
        users = [self.make_user() for _ in range(4)]
        fixture = self.make_fixture(users=users, game=game)
        fixture.rank_set.all().update(rank=2)
        fixture.rank_set.filter(user=users[0]).update(rank=1)
        updates = fixture.calculate_elo_updates()
        self.assertEqual(sum(updates.values()), 0)
        self.assertGreater(updates[users[0]], 0)

    def test_elo_updates__ranked(self):
        game = self.make_game(ranked=True)
        users = [self.make_user() for _ in range(5)]
        fixture = self.make_fixture(users=users, game=game)
        for i, user in enumerate(users):
            fixture.rank_set.filter(user=user).update(rank=i)

        updates = fixture.calculate_elo_updates()
        self.assertEqual(sum(updates.values()), 0)
        self.assertGreater(updates[users[0]], 0)
        self.assertLess(updates[users[-1]], 0)

    def test_elo_updates__tie__same_score(self):
        users = [self.make_user() for _ in range(4)]
        fixture = self.make_fixture(users=users)
        fixture.rank_set.update(rank=1)
        updates = fixture.calculate_elo_updates()
        for update in updates.values():
            self.assertEqual(update, 0)

    def test_elo_updates__tie__different_score(self):
        users = [self.make_user(score=i * 1000) for i in range(4)]
        fixture = self.make_fixture(users=users)
        fixture.rank_set.update(rank=1)
        updates = fixture.calculate_elo_updates()
        self.assertEqual(sum(updates.values()), 0)
        self.assertNotEqual(updates[users[0]], 0)

    def test_apply_elo_updates(self):
        game = self.make_game(ranked=True)
        users = [self.make_user() for _ in range(5)]
        fixture = self.make_fixture(users=users, game=game)
        for i, user in enumerate(users):
            fixture.rank_set.filter(user=user).update(rank=i)
        fixture.finish()
        fixture.apply_elo_updates()
        for user in users:
            user.refresh_from_db()
        scores = {user: user.score for user in users}
        self.assertGreater(scores[users[0]], 1000)
        self.assertLess(scores[users[-1]], 1000)
        self.assertEqual(sum(scores.values()), 5000)

    def test_finish(self):
        fixture = self.make_fixture()
        self.assertIsNone(fixture.ended)
        fixture.finish()
        self.assertIsNotNone(fixture.ended)
        self.assertIsInstance(fixture.ended, datetime.datetime)

    def test_check_constraints(self):
        self.assertRaises(IntegrityError, self.make_fixture, applied=True, ended=None)
