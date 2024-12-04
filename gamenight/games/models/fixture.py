import collections
import datetime
import logging
import math
import uuid
import zoneinfo
from typing import TYPE_CHECKING

from django import urls
from django.db import models

if TYPE_CHECKING:
    from gamenight.games.models.game import Game
    from gamenight.games.models.rank import Rank
    from gamenight.games.models.user import User


class Fixture(models.Model):
    """A fixture between two or more players."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey("games.Game", on_delete=models.CASCADE)
    users = models.ManyToManyField(to="games.User", through="games.Rank")
    started = models.DateTimeField(auto_now_add=True)
    ended = models.DateTimeField(null=True, blank=True)

    applied = models.BooleanField(
        default=False,
        editable=False,
        help_text="Whether the ELO updates have been applied.",
    )

    rank_set: "models.QuerySet[Rank]"

    class Meta:
        constraints = (
            models.CheckConstraint(
                name="applied_requires_ended",
                check=~models.Q(applied=True) | models.Q(ended__isnull=False),
            ),
        )

    def __str__(self) -> str:
        return f"{self.game} with {list(map(str, self.users.all()))}"

    def save(self, *args, **kwargs) -> None:
        """Save the fixture."""
        if self.ended is not None and not self.applied:
            logging.debug("Finishing fixture, applying ELO updates.")
            self.apply_elo_updates()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Get the absolute URL of the fixture."""
        return urls.reverse("fixtures:detail", kwargs={"fixture": self.pk})

    @staticmethod
    def create(game: "Game", users: "list[User]") -> "Fixture":
        """Create a fixture."""
        fixture = Fixture.objects.create(game=game)
        fixture.users.set(users)
        return fixture

    @staticmethod
    def create_url() -> str:
        """Get the URL to create a fixture."""
        return urls.reverse("fixtures:create")

    def get_max_rank(self) -> int:
        """Get the highest rank allowed in this fixture."""
        if not self.game.ranked:
            return 2
        return self.rank_set.count()

    def get_grouped_ranks(self) -> dict[int, list[str]]:
        """Get the ranks of the players in the fixture, grouped by rank."""
        ranks = collections.defaultdict(list)
        for combined in self.get_flat_ranks():
            rank_str, username = combined.split("--", 1)
            rank = int(rank_str)
            ranks[rank].append(username)
        max_rank = self.get_max_rank()
        if max(ranks.keys()) < max_rank:
            for i in range(1, max_rank + 1):
                if i not in ranks:
                    ranks[i] = []
        assert len(ranks.keys()) <= max_rank + 1, f"{ranks=}, {len(ranks)}, {max_rank}"
        return dict(ranks)

    def get_flat_ranks(self) -> "list[str]":
        """Get the ranks of the players in the fixture.

        This produces a special format that can be used in HTML forms.
        """
        return [
            f"{rank.rank}--{rank.user.username}" for rank in self.rank_set.all().order_by("rank")
        ]

    def set_flat_ranks(self, ranks: list[str]) -> None:
        """Update ranks based on the flat ranks from the HTML form."""
        max_rank = self.get_max_rank()
        for combined in ranks:
            rank, user = combined.split("--", 1)
            assert rank.isdigit(), f"{rank=}"
            assert int(rank) <= max_rank, f"{rank=}"
            updated = self.rank_set.filter(user__username=user).update(rank=int(rank))
            assert updated == 1, f"{updated=}"

    def finish(self) -> str:
        """Finish the fixture."""
        assert self.rank_set.filter(rank=0).count() == 0, "there are some unranked players!"
        self.ended = datetime.datetime.now(tz=zoneinfo.ZoneInfo("America/New_York"))
        self.save()
        return self.get_absolute_url()

    def calculate_elo_updates(self) -> "dict[User, int]":
        """Compute ELO updates for every player in the fixture."""
        results = self.rank_set.order_by("rank")
        ranks = collections.defaultdict(list)
        for result in results:
            assert result.rank is not None, f"{result=}"
            ranks[result.rank].append(result.user)

        current_scores = {result.user: result.user.score for result in results}
        updates: dict[User, int] = collections.defaultdict(int)
        players = [r.user for r in results]
        pairwise_dict = {q: {p: 0 for p in players} for q in players}
        for rank_one, players_one in ranks.items():
            for rank_two, players_two in ranks.items():
                for player_one in players_one:
                    for player_two in players_two:
                        if player_one == player_two:
                            continue
                        delta = _elo_delta(
                            self.game,
                            rank_one,
                            current_scores[player_one],
                            rank_two,
                            current_scores[player_two],
                        )
                        pairwise_dict[player_one][player_two] = delta
                        updates[player_one] += delta
        pairwise_table = [
            [pairwise_dict[player_one][player_two] for player_two in players]
            for player_one in players
        ]
        _delta_sums = [sum(row) for row in pairwise_table]
        return updates

    def apply_elo_updates(self) -> None:
        """Apply the ELO updates to the scores of the players."""
        assert self.ended is not None
        if self.applied:
            return
        updates = self.calculate_elo_updates()
        for player, update in updates.items():
            if player.score + update < 0:
                assert player.score + update >= 0, [(p.score, u) for p, u in updates.items()]
            player.score += update
            player.save()
        self.applied = True
        self.save()


def _elo_delta(
    game: "Game",
    rank_one: int,
    score_one: float,
    rank_two: int,
    score_two: float,
) -> int:
    """Compute the ELO update for two players."""
    q1 = 10 ** (score_one / 400)
    q2 = 10 ** (score_two / 400)
    expected_one = q1 / (q1 + q2)
    expected_two = q2 / (q1 + q2)
    assert math.isclose(
        expected_one + expected_two,
        1,
        abs_tol=1e-6,
    ), f"{expected_one=} {expected_two=}"
    update_one = game.importance * (_win_lose_draw(rank_one, rank_two) - expected_one)
    update_two = game.importance * (_win_lose_draw(rank_two, rank_one) - expected_two)
    assert math.isclose(
        math.fabs(update_one + update_two),
        0,
        abs_tol=1e-6,
    ), f"{update_one=} {update_two=}"
    # A game's weight is reduced if the outcome is based on chance.
    # IE, a coinflip game should have a lower weight than a game of darts.
    if game.randomness:
        update_one *= 1 - game.randomness
    return math.trunc(update_one)


def _win_lose_draw(rank_one: int, rank_two: int) -> float:
    """Compute the win/lose/draw probability."""
    if rank_one == rank_two:
        return 0.5
    if rank_one < rank_two:
        return 1
    return 0
