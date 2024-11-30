import uuid

from django.core import validators
from django.db import models


class Game(models.Model):
    """A game to play."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="The name of the game.",
    )
    ranked = models.BooleanField(
        default=False,
        help_text="Whether this game is ranked or win/lose.",
    )
    minimum_players = models.PositiveSmallIntegerField(
        default=2,
        help_text="The minimum number of players required to start a game.",
        validators=[
            validators.MinValueValidator(2),
            validators.MaxValueValidator(50),
        ],
    )
    estimated_duration = models.PositiveSmallIntegerField(
        help_text="The estimated duration of a game in minutes.",
        default=1,
        validators=[
            validators.MinValueValidator(1),
            validators.MaxValueValidator(120),
        ],
    )
    decay = models.FloatField(
        default=0.6,
        help_text="The decay rate for ranked ELO calculations. Only used for ranked games.",
        validators=(
            validators.MinValueValidator(0.0),
            validators.MaxValueValidator(1.0),
        ),
    )

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    @property
    def importance(self) -> int:
        """Compute the importance of the game."""
        return min(self.estimated_duration, 45) + 10
