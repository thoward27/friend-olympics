from gamenight.games.models import User
from tests import base


class TestUser(base.BaseTestCase):
    def test_available__no_fixtures(self):
        [self.make_user() for _ in range(3)]
        self.assertEqual(User.available.all().count(), 3)

    def test_available__with_fixture(self):
        users = [self.make_user() for _ in range(3)]
        self.make_fixture(users=[users[0]])
        self.assertEqual(User.available.all().count(), 2)
