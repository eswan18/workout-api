# Workout API

[![CI](https://github.com/eswan18/workout_api/actions/workflows/ci.yaml/badge.svg)](https://github.com/eswan18/workout_api/actions/workflows/ci.yaml)

An unnecessarily complicated API layer and set of database migrations for my workout tracker application.

API hosted with Render at this URL: `https://workout-api-k8e3.onrender.com/v1`

Database hosted with [Neon](https://neon.tech).

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
# At this point, you may want to set some environment variables for development
. ./local-env.sh
# Start the server in dev mode
make devserve
```

In production, you should set your variables in a more stable way, and then....
```bash
poetry install
poetry run make serve
```


## Database Schema

See here: [link](https://dbdiagram.io/d/63e963d0296d97641d8054fa).
