#!/bin/bash

set -e

uv run python manage.py check

# Reset the Database.
rm -f olympics/games/migrations/0001_initial.py
rm -f db.sqlite3

# Generate and run migrations.
uv run python manage.py makemigrations --no-header
uv run python manage.py migrate

# Test the code.
uv run ruff format
uv run ruff check --fix --ignore T
uv run ruff format
uv run pytest
uv run mypy -p olympics

# Load fixture data.
uv run python manage.py loaddata fixtures/users.json
uv run python manage.py loaddata fixtures/games.json
uv run python manage.py loaddata fixtures/fixtures.json
uv run python manage.py loaddata fixtures/ranks.json

# Run the server.
uv run python manage.py runserver

# Persist data we care to save.
GAMES=`uv run python manage.py dumpdata games.Game`
echo $GAMES | jq --sort-keys > fixtures/games.json
USERS=`uv run python manage.py dumpdata games.User`
echo $USERS | jq --sort-keys > fixtures/users.json
FIXTURES=`uv run python manage.py dumpdata games.Fixture`
echo $FIXTURES | jq --sort-keys > fixtures/fixtures.json
RANKS=`uv run python manage.py dumpdata games.Rank`
echo $RANKS | jq --sort-keys > fixtures/ranks.json
