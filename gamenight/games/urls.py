from django import urls
from django.views import generic
from iommi import path

from gamenight.games import consumers, forms, models, tables, views

path.register_path_decoding(
    game_slug=models.Game.slug,
    fixture=models.Fixture,
)

fixture_patterns = [
    urls.path("", views.FixturePage().as_view(), name="table"),
    urls.path(
        "active/",
        tables.FixtureTable(
            rows=models.Fixture.objects.filter(ended=None).order_by("-started"),
        ).as_view(),
        name="active",
    ),
    urls.path(
        "ended/",
        tables.FixtureTable(
            rows=models.Fixture.objects.exclude(ended=None).order_by("-started"),
        ).as_view(),
        name="ended",
    ),
    urls.path("create/", forms.FixtureCreateForm().as_view(), name="create"),
    urls.path("view/<fixture>/", views.FixtureDetailPage().as_view(), name="detail"),
    urls.path("update/<fixture>/", views.FixtureUpdatePage().as_view(), name="update"),
]


game_patterns = [
    urls.path("", views.GamesPage().as_view(), name="table"),
    urls.path("<game_slug>/", views.GamePage().as_view(), name="detail"),
]


user_patterns = [
    urls.path("", views.UsersPage().as_view(), name="table"),
    urls.path("detail/", views.UserDetailPage().as_view(), name="detail"),
    urls.path("login/token/<str:username>/<str:encrypted_password>", views.qr_login, name="qr"),
]


urlpatterns = [
    urls.path("", generic.RedirectView.as_view(url="/users/")),
    urls.path("users/", urls.include((user_patterns, "users"))),
    urls.path("games/", urls.include((game_patterns, "games"))),
    urls.path("fixtures/", urls.include((fixture_patterns, "fixtures"))),
]

websocket_urlpatterns = [
    urls.re_path(
        r"ws/users/(?P<username>[\w-]+)/score$",
        consumers.UserScoreConsumer.as_asgi(),
        name="ws--user-score",
    ),
]
