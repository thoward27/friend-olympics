from django import urls
from django.views import generic

from olympics.games import tables, views

fixture_patterns = [
    urls.path("", views.FixtureTableView.as_view(), name="table"),
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
    urls.path("table/user", tables.UserTableChunk.as_view(), name="table--user"),
    urls.path("table/game", tables.GameTableChunk.as_view(), name="table--game"),
    urls.path("table/fixture", tables.FixtureTableChunk.as_view(), name="table--fixture"),
]

urlpatterns = [
    urls.path("", generic.RedirectView.as_view(url="/users/")),
    urls.path("users/", urls.include((user_patterns, "users"))),
    urls.path("games/", urls.include((game_patterns, "games"))),
    urls.path("fixtures/", urls.include((fixture_patterns, "fixtures"))),
    urls.path("htmx/", urls.include((htmx_patterns, "htmx"))),
]
