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
    # ARG --required branch
    # ARG --required sha
    COPY --dir fixtures olympics tests manage.py README.md ./
    SAVE IMAGE --push \
        thoward27/friend-olympics:latest
        # thoward27/taylormade:$branch \
        # thoward27/taylormade:$sha
