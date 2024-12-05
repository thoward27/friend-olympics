import iommi
from django import http, template, urls

from gamenight.games import models


def _fixture_update_form__finish__post_handler(
    form: "FixtureUpdateForm",
    fixture: models.Fixture,
    **_,
) -> http.HttpResponse | None:
    if not form.is_valid():
        return None
    fixture.set_flat_ranks(form.fields.users.raw_data)
    fixture.finish()
    return http.HttpResponseRedirect(fixture.get_absolute_url())


class FixtureUpdateForm(iommi.Form):
    title = iommi.Fragment(template=template.Template("<h1>Update Result</h1>"))
    game = iommi.Field.choice(
        choices=lambda fixture, **_: models.Game.objects.filter(
            minimum_players__lte=fixture.users.count(),
            maximum_players__gte=fixture.users.count(),
        ),
        initial=lambda fixture, **_: fixture.game,
    )
    users = iommi.Field(
        extra_evaluated__ranks=lambda fixture, **_: fixture.get_flat_ranks(),
        extra_evaluated__max_rank=lambda fixture, **_: fixture.get_max_rank(),
        extra_evaluated__group_ranks=lambda fixture, **_: fixture.get_grouped_ranks(),
        initial=lambda fixture, **_: fixture.users.count(),
        template="chunk/rank_input.html",
        is_list=True,
        is_valid=lambda parsed_data, **_: (
            not parsed_data.startswith("0"),
            "All players must be ranked",
        ),
    )

    class Meta:
        instance = lambda params, **_: params.fixture  # noqa: E731
        actions__finish = iommi.Action.button(
            attrs__href=".",
            attrs__access_key="s",
            attrs__name=lambda action, **_: action.own_target_marker(),
            attrs__class={"btn-danger": True},
            after="submit",
            post_handler=_fixture_update_form__finish__post_handler,
        )

        @staticmethod
        def actions__submit__post_handler(
            form: "FixtureUpdateForm",
            fixture: models.Fixture,
            **_,
        ) -> http.HttpResponse | None:
            if not form.is_valid():
                return None
            fixture.set_flat_ranks(form.fields.users.raw_data)
            fixture.save()
            return http.HttpResponseRedirect(".")


def create_fixture(form: "FixtureCreateForm", **_) -> http.HttpResponse | None:
    """Create a fixture."""
    if not form.is_valid():
        return None
    fixture = models.Fixture.create(form.fields.game.value, form.fields.users.value)
    return http.HttpResponseRedirect(
        urls.reverse("fixtures:update", kwargs={"fixture": fixture.pk}),
    )


class FixtureCreateForm(iommi.Form):
    title = iommi.Fragment(template=template.Template("<h1>Play a Game</h1>"))
    users = iommi.Field.checkboxes(
        choices=models.User.available.all(),
        required=False,
        input__attrs__class={"form-select": False, "form-control": False},
        attrs__class={"mb-3": False},
    )
    game = iommi.Field.choice_queryset(
        model=models.Game,
        choices=lambda form, **_: models.Game.objects.filter(
            minimum_players__lte=len(form.fields.users.raw_data or [])
            or models.User.objects.count(),
        ),
        is_valid=lambda form, parsed_data, request, **_: (
            request.method == "GET" or parsed_data.can_play(form.fields.users.raw_data),
            "You do not have the right amount of players for this game!",
        ),
    )

    class Meta:
        actions__submit = iommi.Action.submit(
            post_handler=create_fixture,
        )
        extra__is_create = True

    @staticmethod
    def actions__submit__post_handler(
        form: "FixtureCreateForm",
        **_,
    ) -> http.HttpResponse | None:
        if not form.is_valid():
            return None
        fixture = models.Fixture.objects.create(
            game=form.fields.game.value,
        )
        fixture.users.set(form.fields.users.raw_data)
        fixture.save()
        return http.HttpResponseRedirect(".")


class UserChangePasswordForm(iommi.Form):
    class Meta:
        @staticmethod
        def actions__submit__post_handler(
            form: "UserChangePasswordForm",
            request: http.HttpRequest,
            **_,
        ) -> http.HttpResponse | None:
            if not form.is_valid():
                return None
            assert request.user.is_authenticated
            user = cast(models.User, request.user)
            user.set_password(form.fields.new_password.value)
            user.set_qr_code(form.fields.new_password.value)
            user.save()
            auth.update_session_auth_hash(request, user)
            return http.HttpResponseRedirect(".")

    current_password = iommi.Field.password(
        is_valid=views.current_password__is_valid,
        display_name="Current password",
    )
    new_password = iommi.Field.password(
        is_valid=views.new_password__is_valid,
        display_name="New password",
    )
    confirm_password = iommi.Field.password(
        is_valid=views.confirm_password__is_valid,
        display_name="Confirm password",
    )
