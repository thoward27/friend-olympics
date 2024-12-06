from typing import cast

from django import http, template, urls

register = template.Library()


@register.filter
def is_active(request: http.HttpRequest, pattern: str) -> str:
    """Whether the current request is for the given pattern."""
    if pattern in cast(urls.ResolverMatch, request.resolver_match).view_name:
        return "active"
    return ""


@register.filter
def ordinal(number: str | int) -> str:
    """Convert a number to its ordinal form."""
    n = int(number)
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")  # noqa: PLR2004
    return f"{n}{suffix}"
