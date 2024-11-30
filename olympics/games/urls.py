from django import urls
from django.views import generic

from olympics.games import consumers, tables, views

fixture_patterns = [
    urls.path("", views.FixtureTableView.as_view(), name="all"),
    urls.path("active/", views.FixtureTableActiveView.as_view(), name="active"),
    urls.path("ended/", views.FixtureTableEndedView.as_view(), name="ended"),
    urls.path("create/", views.FixtureCreateView.as_view(), name="create"),
    urls.path("view/<uuid:pk>/", views.FixtureDetailView.as_view(), name="detail"),
]

game_patterns = [
    urls.path("", views.GameTableView.as_view(), name="table"),
]

user_patterns = [
    urls.path("", views.UserTableView.as_view(), name="table"),
]

htmx_patterns = [
    urls.path("table/user/", tables.UserTableChunk.as_view(), name="table--user"),
    urls.path("table/game/", tables.GameTableChunk.as_view(), name="table--game"),
    urls.path("table/fixture/", tables.FixtureTableChunk.as_view(), name="table--fixture"),
    urls.path(
        "table/fixture/active",
        tables.FixtureTableActiveChunk.as_view(),
        name="table--fixture-active",
    ),
    urls.path(
        "table/fixture/ended",
        tables.FixtureTableEndedChunk.as_view(),
        name="table--fixture-ended",
    ),
]

urlpatterns = [
    urls.path("", generic.RedirectView.as_view(url="/users/")),
    urls.path("users/", urls.include((user_patterns, "users"))),
    urls.path("games/", urls.include((game_patterns, "games"))),
    urls.path("fixtures/", urls.include((fixture_patterns, "fixtures"))),
    urls.path("htmx/", urls.include((htmx_patterns, "htmx"))),
]

websocket_urlpatterns = [
    urls.re_path(
        r"ws/users/(?P<username>\w+)/score$",
        consumers.UserScoreConsumer.as_asgi(),
        name="ws--user-score",
    ),
]
