from gamenight.games.models.fixture import Fixture
from gamenight.games.models.game import Game
from gamenight.games.models.user import User


def play(game: Game, players: list[User]) -> Fixture:
    """Start a game between players."""
    if not players or len(players) < game.minimum_players:
        raise ValueError("At least two players are required.")
    if Fixture.objects.filter(users__in=players, ended=None).exists():
        raise ValueError("At least one player is already playing a game.")
    fixture = Fixture.objects.create(game=game)
    fixture.users.set(players)
    return fixture


def recompute_all_scores() -> None:
    """Recompute scores for all users."""
    for user in User.objects.all():
        user.score = User.DEFAULT_SCORE
        user.save()
    for fixture in Fixture.objects.filter(ended__isnull=False).order_by("ended"):
        fixture.applied = False
        fixture.apply_player_graph()
