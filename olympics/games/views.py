# Create your views here.
from django.contrib.auth import mixins
from django.views import generic

from olympics.games import forms, models


class UserTableView(generic.TemplateView):
    template_name = "games/user_table.html"


class GameTableView(generic.TemplateView):
    template_name = "games/game_table.html"


class FixtureTableView(generic.TemplateView):
    template_name = "games/fixture_table.html"


class FixtureDetailView(generic.DetailView):
    model = models.Fixture
    template_name = "games/fixture_detail.html"


class FixtureCreateView(mixins.LoginRequiredMixin, generic.CreateView):
    model = models.Fixture
    form_class = forms.FixtureCreateForm
    template_name = "games/fixture_create.html"

