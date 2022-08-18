# Workout API

[![CI](https://github.com/eswan18/workout_api/actions/workflows/ci.yaml/badge.svg)](https://github.com/eswan18/workout_api/actions/workflows/ci.yaml)

This project is built with Poetry and intended to be run that way.
To run it locally in development, install Poetry, and then you can run this code with:

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
