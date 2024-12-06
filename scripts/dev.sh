#!/bin/bash

set -e

uv run python manage.py check

# Reset the Database.
# TODO: Remove migration regeneration once we move to postgres.
rm -f gamenight/games/migrations/0001_initial.py
uv run python manage.py reset_db 

# Generate and run migrations.
uv run python manage.py makemigrations --no-header
uv run python manage.py migrate

# Load fixture data.
uv run python manage.py loaddata fixtures/users.json
uv run python manage.py loaddata fixtures/games.json

# Run the server.
uv run python manage.py runserver

# Persist data we care to save.
GAMES=`uv run python manage.py dumpdata games.Game`
echo $GAMES | jq --sort-keys > fixtures/games.json
USERS=`uv run python manage.py dumpdata games.User`
echo $USERS | jq --sort-keys > fixtures/users.json
