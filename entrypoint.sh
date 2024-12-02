#!/bin/bash

set -e

# Ensure we can run the Django management commands.
uv run python manage.py check

# Migrate the database
uv run python manage.py migrate

# Load fixture data.
uv run python manage.py loaddata fixtures/users.json
uv run python manage.py loaddata fixtures/games.json
uv run python manage.py loaddata fixtures/fixtures.json
uv run python manage.py loaddata fixtures/ranks.json

# Run the command from the user.
uv run python manage.py $@
