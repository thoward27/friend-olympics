# Create your views here.
from django.contrib.auth import mixins
from django.views import generic

from olympics.games import forms, models, tables


class UserTableView(tables.UserTableChunk):
    template_name = "games/user_table.html"


class GameTableView(tables.GameTableChunk):
    template_name = "games/game_table.html"


class FixtureTableView(tables.FixtureTableChunk):
    template_name = "games/fixture_table.html"


class FixtureTableActiveView(tables.FixtureTableActiveChunk):
    template_name = "games/fixture_table_active.html"


class FixtureTableEndedView(tables.FixtureTableEndedChunk):
    template_name = "games/fixture_table_ended.html"


class FixtureDetailView(generic.DetailView):
    model = models.Fixture
    template_name = "games/fixture_detail.html"


class FixtureCreateView(mixins.LoginRequiredMixin, generic.CreateView):
    model = models.Fixture
    form_class = forms.FixtureCreateForm
    template_name = "games/fixture_create.html"
