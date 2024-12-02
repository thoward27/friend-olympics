from gamenight.games.models import utils
from tests import base


class TestPlay(base.BaseTestCase):
    def test_play__no_players(self):
        game = self.make_game()
        self.assertRaises(ValueError, utils.play, game, [])

    def test_play__no_existing_fixture(self):
        game = self.make_game()
        users = [self.make_user() for _ in range(4)]
        fixture = utils.play(game, users)
        self.assertIsNone(fixture.ended)

    def test_play__already_playing(self):
        game = self.make_game()
        users = [self.make_user() for _ in range(4)]
        utils.play(game, users)
        self.assertRaises(ValueError, utils.play, game, users)
