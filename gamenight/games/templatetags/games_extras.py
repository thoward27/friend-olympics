from typing import cast

from django import http, template, urls

register = template.Library()


@register.filter
def is_active(request: http.HttpRequest, pattern: str) -> str:
    """Whether the current request is for the given pattern."""
    if pattern in cast(urls.ResolverMatch, request.resolver_match).view_name:
        return "active"
    return ""
