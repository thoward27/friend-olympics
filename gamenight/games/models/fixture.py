import collections
import datetime
import logging
import math
import uuid
import zoneinfo
from typing import TYPE_CHECKING

import networkx as nx
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

    def get_grouped_ranks(self) -> dict[int, list[dict[str, str]]]:
        """Get the ranks of the players in the fixture, grouped by rank."""
        ranks = collections.defaultdict(list)
        for combined in self.get_flat_ranks():
            rank_str, username, team = combined.split("--", 2)
            rank = int(rank_str)
            ranks[rank].append({"username": username, "team": team})
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
            f"{rank.rank}--{rank.user.username}--{rank.team}"
            for rank in self.rank_set.all().order_by("rank", "user__username")
        ]

    def set_flat_ranks(self, ranks: list[str]) -> None:
        """Update ranks based on the flat ranks from the HTML form."""
        max_rank = self.get_max_rank()
        for combined in ranks:
            rank, user, team = combined.split("--", 2)
            assert rank.isdigit(), f"{rank=}"
            assert int(rank) <= max_rank, f"{rank=}"
            updated = self.rank_set.filter(user__username=user).update(rank=int(rank), team=team)
            assert updated == 1, f"{updated=}"

    def finish(self) -> str:
        """Finish the fixture."""
        assert self.rank_set.filter(rank=0).count() == 0, "there are some unranked players!"
        self.refresh_from_db()
        if self.ended is None:
            logging.debug("Finishing fixture: %s", self.pk)
            self.ended = datetime.datetime.now(tz=zoneinfo.ZoneInfo("America/New_York"))
            self.save(update_fields=["ended"])
            self._apply_player_graph()
            self.save(update_fields=["applied"])
        return self.get_absolute_url()

    def reapply(self) -> None:
        """Reapply the ELO updates."""
        self.applied = False
        self._apply_player_graph()
        self.refresh_from_db()

    def _build_player_graph(self) -> nx.DiGraph:
        """Build the graph of the players in the fixture.

        For every edge (m, n) in the resultant DAG, n gives a non-zero sumo of points to m.
        """
        assert self.rank_set.count() > 1, "Cannot build a graph with less than two players."
        assert not self.rank_set.filter(rank=0).exists(), "Cannot rank unset players."
        graph = nx.DiGraph()
        # Gainers are those gaining points, where losers are ones giving up points.
        for target in self.rank_set.all().order_by("rank", "user__score"):
            sources = (
                # We exclude ourself.
                self.rank_set.exclude(pk=target.pk)
                # As well as any players we have drawn with of *lower or equal* score.
                # If we draw with a player of a lower score, we give *them* points.
                .exclude(
                    models.Q(rank=target.rank) & models.Q(user__score__lte=target.user.score),
                )
                # Find all the players we have beaten.
                .filter(rank__gte=target.rank)
            )
            # Lastly, remove players on the same team (they don't trade points).
            if target.team:
                sources = sources.exclude(team=target.team)
            for source in sources:
                assert target.rank <= source.rank, f"{target.rank=} {source.rank=}"
                delta = _elo_delta(
                    self.game,
                    source.rank,
                    source.user.score,
                    target.rank,
                    target.user.score,
                )
                if delta == 0:
                    continue
                assert delta > 0, f"{delta=}, {target=}, {source=}"
                graph.add_edge(
                    source,
                    target,
                    delta=delta,
                )
        return graph

    def _apply_player_graph(self) -> None:
        """Apply the deltas from the players graph."""
        if self.applied:
            logging.info("ELO updates already applied.")
            return
        graph = self._build_player_graph()
        deltas: dict[Rank, int] = collections.defaultdict(int)
        for gainer, loser, data in graph.edges(data=True):
            delta = data["delta"]
            assert gainer != loser
            assert delta > 0
            deltas[gainer] += delta
            deltas[loser] -= delta
        for rank, delta in deltas.items():
            rank.user.score += delta
            rank.user.save()
        self.applied = True


def _elo_delta(
    game: "Game",
    source_rank: int,
    source_score: float,
    target_rank: int,
    target_score: float,
) -> int:
    """Compute the ELO update for two players."""
    target_q = 10 ** (target_score / 400)
    source_q = 10 ** (source_score / 400)
    target_expected = target_q / (target_q + source_q)
    source_expected = source_q / (target_q + source_q)
    assert math.isclose(
        target_expected + source_expected,
        1,
        abs_tol=1e-6,
    ), f"{target_expected=} {source_expected=}"
    delta = game.importance * (_win_lose_draw(target_rank, source_rank) - target_expected)
    # A game's weight is reduced if the outcome is based on chance.
    # IE, a coinflip game should have a lower weight than a game of darts.
    if game.randomness:
        delta *= 1 - game.randomness / 2
    return math.trunc(delta)


def _win_lose_draw(rank_one: int, rank_two: int) -> float:
    """Compute the win/lose/draw probability."""
    if rank_one == rank_two:
        return 0.5
    if rank_one < rank_two:
        return 1
    return 0
