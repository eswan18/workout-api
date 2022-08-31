FROM python:3.10-bullseye
 
RUN useradd -ms /bin/bash workout-api
USER workout-api
WORKDIR /home/workout-api/workout-api

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python -
# Add it to the path
ENV PATH="${PATH}:/home/workout-api/.local/bin"


ADD ./poetry.lock ./pyproject.toml ./setup.cfg ./

RUN poetry install --only main --no-interaction --no-ansi --no-root

ADD ./Makefile ./
ADD ./app ./app

ENTRYPOINT poetry run make serve
