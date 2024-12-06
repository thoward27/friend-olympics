import datetime
from unittest import mock

from django.db import IntegrityError

from tests import base


class TestFixture(base.BaseTestCase):
    def test_apply_score_updates(self):
        game = self.make_game(ranked=True)
        users = [self.make_user() for _ in range(5)]
        fixture = self.make_fixture(users=users, game=game)
        for i, user in enumerate(users):
            fixture.rank_set.filter(user=user).update(rank=i + 1)
        fixture.finish()
        for user in users:
            user.refresh_from_db()
        scores = {user: user.score for user in users}
        self.assertGreater(scores[users[0]], 1000)
        self.assertLess(scores[users[-1]], 1000)
        self.assertEqual(sum(scores.values()), 5000)

    @mock.patch("gamenight.games.models.fixture.logging.debug", autospec=True)
    def test_finish(self, debug_mock):
        fixture = self.make_fixture(users=[self.make_user() for _ in range(4)], rank_users=True)
        self.assertIsNone(fixture.ended)
        fixture.finish()
        self.assertIsNotNone(fixture.ended)
        self.assertIsInstance(fixture.ended, datetime.datetime)
        debug_mock.assert_has_calls([mock.call("Finishing fixture: %s", fixture.pk)])
        ended = fixture.ended
        fixture.finish()
        self.assertEqual(fixture.ended, ended)

    def test_check_constraints(self):
        self.assertRaises(IntegrityError, self.make_fixture, applied=True, ended=None)

    def test_get_grouped_ranks(self):
        game = self.make_game(ranked=True)
        users = [self.make_user(username=f"user{i}") for i in range(5)]
        fixture = self.make_fixture(users=users, game=game)
        self.assertEqual(
            fixture.get_grouped_ranks(),
            {0: ["user0", "user1", "user2", "user3", "user4"], 1: [], 2: [], 3: [], 4: [], 5: []},
        )
        fixture.set_flat_ranks(["1--user4", "2--user3", "3--user2", "4--user1", "5--user0"])
        self.assertEqual(
            fixture.get_grouped_ranks(),
            {1: ["user4"], 2: ["user3"], 3: ["user2"], 4: ["user1"], 5: ["user0"]},
        )

    def test_flat_ranks__good(self):
        game = self.make_game(ranked=True)
        users = [self.make_user(username=f"user{i}") for i in range(5)]
        fixture = self.make_fixture(users=users, game=game)
        self.assertEqual(
            fixture.get_flat_ranks(),
            ["0--user0", "0--user1", "0--user2", "0--user3", "0--user4"],
        )
        fixture.set_flat_ranks(["1--user4", "2--user3", "3--user2", "4--user1", "5--user0"])
        self.assertEqual(
            fixture.get_flat_ranks(),
            ["1--user4", "2--user3", "3--user2", "4--user1", "5--user0"],
        )

    def test_flat_ranks__bad(self):
        game = self.make_game(ranked=True)
        users = [self.make_user(username=f"user{i}") for i in range(3)]
        fixture = self.make_fixture(users=users, game=game)
        self.assertEqual(fixture.get_flat_ranks(), ["0--user0", "0--user1", "0--user2"])
        self.assertRaises(
            AssertionError,
            fixture.set_flat_ranks,
            ["4--user0", "0--user1", "0--user2"],
        )

    def test_get_max_rank(self):
        game = self.make_game(ranked=True)
        users = [self.make_user(username=f"user{i}") for i in range(5)]
        fixture = self.make_fixture(users=users, game=game)
        self.assertEqual(fixture.get_max_rank(), 5)
        game = self.make_game(ranked=False)
        fixture = self.make_fixture(users=users, game=game)
        self.assertEqual(fixture.get_max_rank(), 2)

    def test_build_graph__ranked__no_ties(self):
        # For this test, we have 5 users, each with their own rank.
        users = [self.make_user(username=f"user{i}") for i in range(5)]
        fixture = self.make_fixture(users=users, game=self.make_game(ranked=True))
        for i, user in enumerate(users):
            fixture.rank_set.filter(user=user).update(rank=i + 1)
        graph = fixture._build_player_graph()
        self.assertEqual(graph.number_of_edges(), 10)
        self.assertEqual(graph.number_of_nodes(), 5)
        self.assertTrue(all(gainer.rank < loser.rank for gainer, loser in graph.edges()))
        self.assertTrue(all(data["delta"] > 0 for _, _, data in graph.edges(data=True)))
        # If we move two players to a team, then the rest to another, we should have 6 edges.
        fixture.rank_set.filter(rank__in=[1, 2]).update(team="team1")
        fixture.rank_set.filter(rank__in=[3, 4, 5]).update(team="team2")
        graph = fixture._build_player_graph()
        self.assertEqual(graph.number_of_edges(), 6)
        self.assertEqual(graph.number_of_nodes(), 5)

    def test_build_graph__ranked__tied(self):
        # For this test, we have 5 users, each with their own unique score, one player with 0.
        users = [self.make_user(username=f"user{i}", score=1000 * i) for i in range(5)]
        fixture = self.make_fixture(users=users, game=self.make_game(ranked=True))
        # And, they all tie, somehow.
        fixture.rank_set.update(rank=1)
        graph = fixture._build_player_graph()
        # This should make a fully-connected graph.
        self.assertEqual(graph.number_of_edges(), 5 * (5 - 1) / 2)

    def test_build_graph__ranked__no_ties__teams(self):
        users = [self.make_user(username=f"user{i}") for i in range(5)]
        fixture = self.make_fixture(users=users)
        for i, user in enumerate(users):
            fixture.rank_set.filter(user=user).update(rank=i + 1, team="odd" if i % 2 else "even")
        graph = fixture._build_player_graph()
        self.assertEqual(graph.number_of_edges(), 6)
        self.assertEqual(graph.number_of_nodes(), 5)
        last_delta = None
        for gainer, loser, data in graph.edges(data=True):
            self.assertLess(gainer.rank, loser.rank)
            self.assertGreater(data["delta"], 0)
            if last_delta is not None:
                self.assertEqual(data["delta"], last_delta)
