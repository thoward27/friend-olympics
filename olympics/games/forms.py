from typing import Any, cast

from django import forms

from olympics.games import models


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
