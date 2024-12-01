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
    from olympics.games.models.game import Game
    from olympics.games.models.rank import Rank
    from olympics.games.models.user import User


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
            logging.warning("Finishing fixture, applying ELO updates.")
            self.apply_elo_updates()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Get the absolute URL of the fixture."""
        return urls.reverse("fixtures:detail", kwargs={"pk": self.pk})

    def finish(self) -> None:
        """Finish the fixture."""
        self.ended = datetime.datetime.now(tz=zoneinfo.ZoneInfo("America/New_York"))
        self.save()

    def calculate_elo_updates(self) -> "dict[User, int]":
        """Compute ELO updates for every player in the fixture."""
        results = self.rank_set.order_by("rank")
        ranks = collections.defaultdict(list)
        for result in results:
            assert result.rank is not None, f"{result=}"
            ranks[result.rank].append(result.user)

        current_scores = {result.user: result.user.score for result in results}
        updates: dict[User, int] = collections.defaultdict(int)
        for rank_one, players_one in ranks.items():
            for rank_two, players_two in ranks.items():
                if rank_one > rank_two:
                    continue
                for player_one in players_one:
                    for player_two in players_two:
                        if player_one == player_two:
                            continue
                        delta_player_one, delta_player_two = _elo_delta(
                            self.game,
                            rank_one,
                            current_scores[player_one],
                            rank_two,
                            current_scores[player_two],
                        )
                        updates[player_one] += delta_player_one
                        updates[player_two] += delta_player_two
            if not self.game.ranked:
                # If this game is win/lose, then we do not compute the partial updates.
                break
        return updates

    def apply_elo_updates(self) -> None:
        """Apply the ELO updates to the scores of the players."""
        assert self.ended is not None
        if self.applied:
            return
        updates = self.calculate_elo_updates()
        for player, update in updates.items():
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
) -> tuple[int, int]:
    """Compute the ELO update for two players."""
    assert game.ranked or rank_one == 1
    assert rank_one <= rank_two, f"{rank_one} is not greater than or equal to {rank_two}"
    prob_one = 1 / (1 + 10 ** ((score_one - score_two) / 400))
    prob_two = 1 / (1 + 10 ** ((score_two - score_one) / 400))
    update_one = game.importance * (_win_lose_draw(rank_one, rank_two) - prob_one)
    update_two = game.importance * (_win_lose_draw(rank_two, rank_one) - prob_two)
    if (diff := abs(rank_one - rank_two)) > 1:
        # If the ranks are more than one apart, then the decay rate is applied.
        update_one *= game.decay**diff
        update_two *= game.decay**diff
    # A game's weight is reduced if the outcome is based on chance.
    # IE, a coinflip game should have a lower weight than a game of darts.
    if game.randomness:
        update_one *= 1 - game.randomness
        update_two *= 1 - game.randomness
    update_one = math.trunc(update_one)
    update_two = math.trunc(update_two)
    assert update_one + update_two == 0, f"{update_one=} {update_two=}"
    return update_one, update_two


def _win_lose_draw(rank_one: int, rank_two: int) -> float:
    """Compute the win/lose/draw probability."""
    if rank_one == rank_two:
        return 0.5
    if rank_one < rank_two:
        return 1
    return 0
