import iommi
from django import http, template

from gamenight.games import models


class FixtureUpdateForm(iommi.Form):
    title = iommi.Fragment(template=template.Template("<h1>Update Result</h1>"))
    game = iommi.Field.choice(
        choices=lambda fixture, **_: models.Game.objects.filter(
            minimum_players__gte=fixture.users.count(),
            maximum_players__gt=fixture.users.count(),
        ),
    )
    users = iommi.Field(
        extra_evaluated__ranks=lambda fixture, **_: fixture.get_flat_ranks(),
        initial=lambda fixture, **_: fixture.users.count(),
        template="chunk/rank_input.html",
        is_list=True,
    )

    class Meta:
        instance = lambda params, **_: params.fixture  # noqa: E731
        actions__finish = iommi.Action.button(
            attrs__href="/",
            attrs__class={"btn-danger": True},
            after="submit",
            post_handler=lambda **_: http.HttpResponseRedirect("/"),
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
