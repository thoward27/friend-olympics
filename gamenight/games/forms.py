import logging
from typing import Any, cast

from django import forms
from django.http import QueryDict
from django.template import loader
from django.utils import safestring

from gamenight.games import models


class FixtureCreateForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=models.User.available.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = models.Fixture
        fields = ("game", "users")

    def clean(self) -> dict[str, Any]:
        if len(self.cleaned_data["users"]) < (game := self.cleaned_data["game"]).minimum_players:
            self.add_error(
                "users",
                forms.ValidationError(
                    f"This game requires at least {game.minimum_players} players.",
                ),
            )
        return cast(dict, super().clean())


class RankInput(forms.MultipleHiddenInput):
    input_type = "rank"
    template_name = "chunk/rank_input.html"

    def get_context(
        self,
        name: str,
        value: list[int],
        attrs: dict[str, Any] | None,
    ) -> dict[str, Any]:
        context = super().get_context(name, value, attrs)
        context["ranks"] = models.Rank.objects.filter(pk__in=value)
        context["game"] = context["ranks"][0].fixture.game
        return context

    def render(  # type: ignore[override]
        self,
        name: str,
        value: list[int],
        attrs: dict[str, bool | str],
        *_,
        **__,
    ) -> safestring.SafeString | str:
        context = self.get_context(name, value, attrs)
        return loader.get_template(self.template_name).render(context)


class FixtureUpdateForm(forms.ModelForm):
    data: QueryDict

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.initial["users"] = models.Rank.objects.filter(fixture=self.instance)  # type: ignore[index]
        self.fields["users"].queryset = models.Rank.objects.filter(fixture=self.instance)  # type: ignore[attr-defined]

    class Meta:
        model = models.Fixture
        fields = ("game", "users", "ended")
        widgets = {
            "ended": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "users": RankInput(),
        }

    def clean(self) -> dict[str, Any]:
        if self.instance.applied:
            self.add_error(
                None,
                forms.ValidationError(
                    "This fixture cannot be edited because it has already been applied.",
                ),
            )
        if len(self.cleaned_data["users"]) < (game := self.cleaned_data["game"]).minimum_players:
            self.add_error(
                "users",
                forms.ValidationError(
                    f"This game requires at least {game.minimum_players} players.",
                ),
            )
        return cast(dict, super().clean())

    def save(self, commit: bool = True) -> "FixtureUpdateForm":  # noqa: FBT001, FBT002
        count = 0
        if "users" in self.cleaned_data:
            for i, rank_pk in enumerate(self.data.getlist("users")):
                count += self.instance.rank_set.filter(pk=rank_pk).update(rank=i + 1)
            self.cleaned_data.pop("users")
            logging.error("Updated %d ranks.", count)
        return super().save(commit)
