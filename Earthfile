VERSION 0.8
FROM python:3.13-slim
WORKDIR /usr/src/app

RUN apt-get update -qq \
    && apt-get upgrade -qq \
    && apt-get install -qq -y curl

RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && ln -s $HOME/.local/bin/uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync

build:
    ARG --required EARTHLY_GIT_BRANCH
    ARG --required EARTHLY_GIT_HASH
    COPY --dir fixtures gamenight tests entrypoint.sh manage.py README.md ./
    ENTRYPOINT ["./entrypoint.sh"]
    CMD ["uv", "run", "daphne", "--bind=0.0.0.0", "--port=8000", "gamenight.asgi:application"]
    EXPOSE 8000
    SAVE IMAGE --push \
        thoward27/gamenight:latest \
        thoward27/gamenight:$EARTHLY_GIT_HASH \
        thoward27/gamenight:$EARTHLY_GIT_BRANCH

build-all-platforms:
    BUILD --platform=linux/amd64 --platform=linux/arm64 +build

test:
    RUN uv run ruff format --check \
        && uv run ruff check \
        && uv run python manage.py check \
        && uv run python manage.py makemigrations --check \
        && uv run python manage.py test \
        && uv run mypy -p gamenight
