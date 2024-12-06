from gamenight.games.templatetags import games_extras
from tests import base


class TestOrdinal(base.BaseTestCase):
    def test(self):
        self.assertEqual(games_extras.ordinal(1), "1st")
        self.assertEqual(games_extras.ordinal(2), "2nd")
        self.assertEqual(games_extras.ordinal(3), "3rd")
        self.assertEqual(games_extras.ordinal(4), "4th")
        self.assertEqual(games_extras.ordinal(5), "5th")
        self.assertEqual(games_extras.ordinal(6), "6th")
        self.assertEqual(games_extras.ordinal(7), "7th")
        self.assertEqual(games_extras.ordinal(8), "8th")
        self.assertEqual(games_extras.ordinal(9), "9th")
        self.assertEqual(games_extras.ordinal(10), "10th")
        self.assertEqual(games_extras.ordinal(11), "11th")
        self.assertEqual(games_extras.ordinal(12), "12th")
        self.assertEqual(games_extras.ordinal(13), "13th")
        self.assertEqual(games_extras.ordinal(14), "14th")
        self.assertEqual(games_extras.ordinal(15), "15th")
        self.assertEqual(games_extras.ordinal(16), "16th")
        self.assertEqual(games_extras.ordinal(17), "17th")
        self.assertEqual(games_extras.ordinal(18), "18th")
        self.assertEqual(games_extras.ordinal(19), "19th")
        self.assertEqual(games_extras.ordinal(20), "20th")
        self.assertEqual(games_extras.ordinal(21), "21st")
        self.assertEqual(games_extras.ordinal(22), "22nd")
        self.assertEqual(games_extras.ordinal(23), "23rd")
        self.assertEqual(games_extras.ordinal(24), "24th")
