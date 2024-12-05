import uuid

from django import urls
from django.core import validators
from django.db import models
from django.utils import text


class Game(models.Model):
    """A game to play."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="The name of the game.",
    )
    slug = models.SlugField(unique=True, blank=True, help_text="The slug of the game.")
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
    maximum_players = models.PositiveSmallIntegerField(
        default=None,
        null=True,
        blank=True,
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
    randomness = models.FloatField(
        default=0.0,
        help_text="The randomness factor for ranked ELO calculations.",
        validators=(
            validators.MinValueValidator(0.0),
            validators.MaxValueValidator(1.0),
        ),
    )
    objective = models.TextField(
        blank=True,
        null=False,
        default="",
        help_text="The objective of the game.",
    )
    setup = models.TextField(
        blank=True,
        null=False,
        default="",
        help_text="The setup of the game.",
    )
    gameplay = models.TextField(
        blank=True,
        null=False,
        default="",
        help_text="The gameplay of the game.",
    )
    tips_and_strategies = models.TextField(
        blank=True,
        null=False,
        default="",
        help_text="Tips and strategies for playing the game.",
    )

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        self.slug = self.slug or text.slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Get the absolute URL of the game."""
        return urls.reverse("games:detail", kwargs={"game_slug": self.slug})

    @property
    def importance(self) -> int:
        """Compute the importance of the game."""
        return min(self.estimated_duration, 45) + 10

    def can_play(self, players: list) -> bool:
        """Check if the game can be played by the given players."""
        if self.maximum_players is None:
            return self.minimum_players <= len(players)
        return self.minimum_players <= len(players) <= self.maximum_players
