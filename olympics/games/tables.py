from django.db.models.query import QuerySet
from django_tables2 import (  # type: ignore[import]
    tables,
    views,
)

from olympics.games import models


class UserTable(tables.Table):
    score = tables.columns.TemplateColumn(template_name="chunk/score.html")

    class Meta:
        model = models.User
        fields = ("username", "score")
        order_by = "-score"


class UserTableChunk(views.SingleTableView):
    model = models.User
    table_class = UserTable
    template_name = "table.html"


class GameTable(tables.Table):
    class Meta:
        model = models.Game
        fields = ("name", "minimum_players", "ranked", "estimated_duration")


class GameTableChunk(views.SingleTableView):
    model = models.Game
    table_class = GameTable
    template_name = "table.html"


class FixtureTable(tables.Table):
    pk = tables.columns.Column(linkify=True, orderable=False, verbose_name="View")

    def render_pk(self, *_, **__) -> str:
        return "view"

    class Meta:
        model = models.Fixture
        fields = ("pk", "game", "users", "started", "ended")


class FixtureTableChunk(views.SingleTableView):
    model = models.Fixture
    table_class = FixtureTable
    template_name = "table.html"


class FixtureTableActiveChunk(FixtureTableChunk):
    def get_queryset(self) -> QuerySet[views.Any]:
        return super().get_queryset().filter(ended__isnull=True)


class FixtureTableEndedChunk(FixtureTableChunk):
    def get_queryset(self) -> QuerySet[views.Any]:
        return super().get_queryset().filter(ended__isnull=False)
