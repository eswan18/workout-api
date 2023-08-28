# Workout API

[![CI](https://github.com/eswan18/workout_api/actions/workflows/ci.yaml/badge.svg)](https://github.com/eswan18/workout_api/actions/workflows/ci.yaml)

An unnecessarily complicated API layer and set of database migrations for my workout tracker application.
Can be accessed at this link: `https://workout-api-k8e3.onrender.com/v1`

## Tech Overview

- Built with Python, FastAPI, and SQLAlchemy/Alembic. Tested with Pytest.
- API hosted with [Render](https://render.com).
- Database hosted with [Neon](https://neon.tech).
- Secrets managed in [Infisical](https://infisical.com).

## Running the code

This project is built with Poetry and intended to be run that way.
To run it locally in development you'll need to
- Install Poetry
- Install the `psql` CLI
  - On Mac this can be done via Homebrew: `brew install libpq` and then add the installed bin folder to your path

Then run the following code:

```bash
# Install the project and dependencies
poetry install
# Start a new shell within the poetry environment
poetry shell
# At this point, you may want to set some dummy environment variables for development
. ./local-env.sh
# Start the server in dev mode
make devserve
```

# Database Management

There are really just two commands that matter for managing the staging and prod databases. Note that the first one uses the Python environment, so you should run `poetry shell` before kicking these off. Both rely on the `$DATABASE_URL` environment variable.

```bash
# Run all new migrations.
alembic upgrade head
# Drop and replace all views with current definitions.
./db/run_views.sh
```

To run them easily against the staging/prod environments, I just use `infisical run`:

```bash
infisical run --env prod -- alembic upgrade head
infisical run --env prod -- ./db/run_views.sh
```

These two commands are enough to bring a database up to schema parity. They ignore seeds though, which are mentioned below.

## Seeds

I have a few "seed" data records in this repo because in early development I needed some data. You can run them with:

```bash
./db/run_seeds.sh
```

It's possible to run them in staging/prod too, but that should only be done once (the records have hardcoded IDs so new ones will collide) and really isn't even necessary.

```bash
infisical run --env prod -- ./db/run_seeds.sh
```

## Database Schema

The original model is here: [link](https://dbdiagram.io/d/63e963d0296d97641d8054fa).

