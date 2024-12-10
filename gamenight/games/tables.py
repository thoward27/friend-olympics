import iommi
from django import template
from django.templatetags import static

from gamenight.games import models

# Some helpful column templates.
timesince = template.Template("<td>{% if value %}{{ value|timesince }} ago{% endif %}</td>")


class UserTable(iommi.Table):
    username = iommi.Column()
    score = iommi.Column.number(cell__template="chunk/score.html")

    class Meta:
        assets__leaderboard_css = iommi.Asset.css(
            attrs__href=static.static("games/leaderboard.css"),
        )
        rows = models.User.objects.all().order_by("-score")
        title = "Leaderboard"
        page_size = 30
        attrs = {"_": "on htmx:wsAfterMessage call sortTable()"}


class GameTable(iommi.Table):
    name = iommi.Column(cell__url=lambda row, **_: row.get_absolute_url())
    players = iommi.Column(
        cell__value=lambda row, **_: f"{row.minimum_players} - {row.maximum_players}",
        sortable=False,
        # TODO: How can we filter on someone just saying "I have 2 players?"
        filter__include=False,
        cell__attrs__class={"d-md-none": True},
        header__attrs__class={"d-md-none": True},
    )
    minimum_players = iommi.Column.number(
        filter__include=True,
        filter__query_operator_for_field=">=",
        filter__field__call_target__attribute="integer",
        filter__parse=lambda string_value, **_: int(string_value),
        display_name="Min players",
        cell__attrs__class={"d-none": True, "d-md-table-cell": True},
        header__attrs__class={"d-none": True, "d-md-table-cell": True},
    )
    maximum_players = iommi.Column.number(
        filter__include=True,
        filter__query_operator_for_field="<=",
        display_name="Max players",
        cell__attrs__class={"d-none": True, "d-md-table-cell": True},
        header__attrs__class={"d-none": True, "d-md-table-cell": True},
    )
    estimated_duration = iommi.Column.number(
        cell__attrs__class={"d-none": True, "d-md-table-cell": True},
        header__attrs__class={"d-none": True, "d-md-table-cell": True},
    )
    ranked = iommi.Column.boolean(
        filter__include=True,
        cell__attrs__class={"d-none": True, "d-md-table-cell": True},
        header__attrs__class={"d-none": True, "d-md-table-cell": True},
    )
    # TODO: Play link from each game.
    # play = iommi.Column.link(cell__uddrl=lambda )

    class Meta:
        rows = models.Game.objects.all()
        title = "Games"
        page_size = 30


class FixtureTable(iommi.Table):
    view = iommi.Column(
        cell__url=lambda row, **_: row.get_absolute_url(),
        cell__value="view",
        sortable=False,
    )
    game = iommi.Column.foreign_key(
        models.Fixture.game.field,
        filter__call_target__attribute="choice",
        filter__include=True,
    )
    users = iommi.Column.many_to_many(
        models.Fixture.users.field,
        filter__call_target__attribute="choice",
        filter__include=True,
    )
    started = iommi.Column.datetime(cell__template=timesince)
    ended = iommi.Column.datetime(cell__template=timesince)

    class Meta:
        rows = models.Fixture.objects.all().distinct()
        title = "Results"
        page_size = 30
        actions__create = iommi.Action(attrs__href=lambda **_: models.Fixture.create_url())
