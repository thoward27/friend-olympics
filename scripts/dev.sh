#!/bin/bash

set -e

uv run python manage.py check

# Generate and format migrations
uv run python manage.py makemigrations --no-header
uv run ruff check --fix --ignore T
uv run ruff format
uv run ruff check --fix --ignore T
uv run ruff format

# Run migrations.
uv run python manage.py migrate

# Load fixture data.
uv run python manage.py loaddata fixtures/users.json
uv run python manage.py loaddata fixtures/games.json

# Run the server.
uv run python manage.py runserver

# Persist data we care to save.
GAMES=`uv run python manage.py dumpdata games.Game`
echo $GAMES | jq --sort-keys > fixtures/games.json
