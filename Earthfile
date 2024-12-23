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

prepare:
    ARG --required EARTHLY_GIT_BRANCH
    ARG --required EARTHLY_GIT_HASH
    COPY --dir fixtures gamenight tests scripts manage.py README.md ./
    RUN uv run python manage.py collectstatic --noinput
    ENTRYPOINT ["./scripts/entrypoint.sh"]
    CMD ["uv", "run", "daphne", "--bind=0.0.0.0", "--port=8000", "gamenight.asgi:application"]
    EXPOSE 8000
    SAVE IMAGE --push \
        thoward27/gamenight:latest \
        thoward27/gamenight:$EARTHLY_GIT_HASH \
        thoward27/gamenight:$EARTHLY_GIT_BRANCH

build:
    WAIT
        BUILD +prepare
    END
    LOCALLY
    WITH DOCKER --load gamenight:earthly=+prepare
        RUN docker run --network host --rm gamenight:earthly uv run python manage.py check
    END

publish:
    BUILD --platform=linux/amd64 --platform=linux/arm64 +prepare

test:
    RUN uv run ruff format --check \
        && uv run ruff check \
        && uv run python manage.py check \
        && uv run python manage.py makemigrations --check \
        && uv run python manage.py test \
        && uv run mypy -p gamenight
