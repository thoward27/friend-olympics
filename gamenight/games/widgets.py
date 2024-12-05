from django import forms
from django.utils import safestring


class Base64ImageWidget(forms.widgets.Widget):
    def render(self, name: str, value: str, **_) -> safestring.SafeString:  # type: ignore[override]
        return safestring.mark_safe(  # noqa: S308
            f'<img src="data:image/png;base64,{value}" name={name} width="200" height="200" />',
        )
