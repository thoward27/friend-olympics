import datetime

from gamenight.games.models import User
from tests import base


class TestUser(base.BaseTestCase):
    def test_available__no_fixtures(self):
        [self.make_user() for _ in range(3)]
        self.assertEqual(User.available.all().count(), 3)

    def test_available__with_fixture(self):
        users = [self.make_user() for _ in range(4)]
        fixture = self.make_fixture(users=users[:2], rank_users=True)
        self.assertEqual(User.available.all().count(), 2)
        fixture.ended = datetime.datetime.now(tz=datetime.UTC)
        fixture.save()
        self.assertEqual(User.available.all().count(), 4)
        self.make_fixture(users=users[:2])
        self.assertEqual(User.available.all().count(), 2)

    def test_set_password(self):
        user = self.make_user()
        user.set_password("123456")
        user.save()
        self.assertNotEqual(user.qrcode, "")
