# Create your views here.
import logging
from cryptography import fernet
from django import http
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import mixins
from django.views import generic

from olympics.games import forms, models, tables


def login(request: http.HttpRequest, username: str, encrypted_password: str) -> http.HttpResponse:
    """Login to the olympics portal.

    This is an insane way to do this, but it allows users to login by scanning their QR code.
    """
    user = models.User.objects.get(username=username)
    password = fernet.Fernet(settings.FERNET_KEY).decrypt(encrypted_password.encode())
    if user.check_password(password.decode()):
        auth.login(request, user)
    else:
        logging.error("Failed to login user %s %s", username, password)
    return http.HttpResponseRedirect("/")


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


class FixtureUpdateView(mixins.LoginRequiredMixin, generic.UpdateView):
    model = models.Fixture
    template_name = "games/fixture_update.html"
    form_class = forms.FixtureUpdateForm

    def form_valid(self, form: forms.FixtureUpdateForm) -> http.HttpResponse:
        response = super().form_valid(form)
        form.save()
        return response
