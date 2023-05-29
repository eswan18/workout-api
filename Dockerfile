# Builder image: create a virtualenv with poetry
FROM python:3.11-bullseye AS builder

RUN useradd -ms /bin/bash workout-api
USER workout-api
 
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_HOME=/home/workout-api/.poetry

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN ${POETRY_HOME}/bin/poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR


FROM python:3.11-slim-bullseye AS runtime

# Copy the virtual env from the builder and add it to the path.
ENV VIRTUAL_ENV=/app/.venv PATH="/app/.venv/bin:$PATH"
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app
ADD ./setup.cfg ./alembic.ini ./
COPY ./app ./app
COPY ./alembic ./alembic

ENTRYPOINT uvicorn app.main:app --host 0.0.0.0
