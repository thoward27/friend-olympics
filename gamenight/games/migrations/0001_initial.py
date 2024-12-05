import uuid

import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Game",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="The name of the game.",
                        max_length=100,
                        unique=True,
                    ),
                ),
                (
                    "slug",
                    models.SlugField(blank=True, help_text="The slug of the game.", unique=True),
                ),
                (
                    "ranked",
                    models.BooleanField(
                        default=False,
                        help_text="Whether this game is ranked or win/lose.",
                    ),
                ),
                (
                    "minimum_players",
                    models.PositiveSmallIntegerField(
                        default=2,
                        help_text="The minimum number of players required to start a game.",
                        validators=[
                            django.core.validators.MinValueValidator(2),
                            django.core.validators.MaxValueValidator(50),
                        ],
                    ),
                ),
                (
                    "maximum_players",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        default=None,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(2),
                            django.core.validators.MaxValueValidator(50),
                        ],
                    ),
                ),
                (
                    "estimated_duration",
                    models.PositiveSmallIntegerField(
                        default=1,
                        help_text="The estimated duration of a game in minutes.",
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(120),
                        ],
                    ),
                ),
                (
                    "decay",
                    models.FloatField(
                        default=0.6,
                        help_text="The decay rate for ranked ELO calculations. Only used for ranked games.",
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                            django.core.validators.MaxValueValidator(1.0),
                        ],
                    ),
                ),
                (
                    "randomness",
                    models.FloatField(
                        default=0.0,
                        help_text="The randomness factor for ranked ELO calculations.",
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                            django.core.validators.MaxValueValidator(1.0),
                        ],
                    ),
                ),
                (
                    "objective",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="The objective of the game.",
                    ),
                ),
                (
                    "setup",
                    models.TextField(blank=True, default="", help_text="The setup of the game."),
                ),
                (
                    "gameplay",
                    models.TextField(blank=True, default="", help_text="The gameplay of the game."),
                ),
                (
                    "tips_and_strategies",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Tips and strategies for playing the game.",
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(blank=True, null=True, verbose_name="last login"),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={"unique": "A user with that username already exists."},
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(blank=True, max_length=150, verbose_name="first name"),
                ),
                (
                    "last_name",
                    models.CharField(blank=True, max_length=150, verbose_name="last name"),
                ),
                (
                    "email",
                    models.EmailField(blank=True, max_length=254, verbose_name="email address"),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="date joined",
                    ),
                ),
                ("score", models.PositiveIntegerField(default=1000)),
                ("qr_code", models.URLField(blank=True, default="")),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "ordering": ("username",),
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Fixture",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("started", models.DateTimeField(auto_now_add=True)),
                ("ended", models.DateTimeField(blank=True, null=True)),
                (
                    "applied",
                    models.BooleanField(
                        default=False,
                        editable=False,
                        help_text="Whether the ELO updates have been applied.",
                    ),
                ),
                (
                    "game",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="games.game"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Rank",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "rank",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        default=0,
                        help_text="The rank of the individual player in a fixture.",
                    ),
                ),
                (
                    "team",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="The team the player is on. If empty, the player is not on a team.",
                        max_length=100,
                    ),
                ),
                (
                    "fixture",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="games.fixture",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("rank",),
            },
        ),
        migrations.AddField(
            model_name="fixture",
            name="users",
            field=models.ManyToManyField(through="games.Rank", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name="rank",
            constraint=models.UniqueConstraint(fields=("user", "fixture"), name="unique_rank"),
        ),
        migrations.AddConstraint(
            model_name="fixture",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(("applied", True), _negated=True),
                    ("ended__isnull", False),
                    _connector="OR",
                ),
                name="applied_requires_ended",
            ),
        ),
    ]
