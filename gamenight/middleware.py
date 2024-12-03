import fnmatch
from collections.abc import Callable
from urllib.parse import urlparse

from django import http
from django.conf import settings
from django.contrib.auth import middleware
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import resolve_url


class LoginRequiredMiddleware(middleware.LoginRequiredMiddleware):  # type: ignore[name-defined]
    """Middleware that redirects all unauthenticated requests to a login page.

    Views using the login_not_required decorator will not be redirected.
    """

    def handle_no_permission(
        self,
        request: http.HttpRequest,
        view_func: Callable,
    ) -> http.HttpResponse | None:
        uri = request.build_absolute_uri()
        path = urlparse(uri).path
        for public_path in settings.PUBLIC_PATHS:
            if fnmatch.fnmatch(path, public_path):
                return None

        resolved_login_url = resolve_url(self.get_login_url(view_func))
        # If the login url is the same scheme and net location then use the
        # path as the "next" url.
        login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
        current_scheme, current_netloc = urlparse(uri)[:2]
        if (not login_scheme or login_scheme == current_scheme) and (
            not login_netloc or login_netloc == current_netloc
        ):
            uri = request.get_full_path()

        return redirect_to_login(
            uri,
            resolved_login_url,
            self.get_redirect_field_name(view_func),
        )
