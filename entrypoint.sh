#!/bin/bash

set -e

export DJANGO_SETTINGS_MODULE=gamenight.settings

# Ensure we can run the Django management commands.
uv run python manage.py check

# Migrate the database
uv run python manage.py migrate

# Load fixture data.
uv run python manage.py loaddata fixtures/users.json
uv run python manage.py loaddata fixtures/games.json

# Run the command from the user.
# uv run daphne -b 0.0.0.0 -p 8000 gamenight.asgi:application "$@"
exec "$@"
