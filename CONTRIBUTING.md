# Contributing

*(These are just mostly notes to myself)*

## Alembic

## Running Migrations

The vast majority of the time, `alembic upgrade head` is all you need; this runs all migrations that aren't currently applied to the database.

### Autogenerating Migrations

After changing the model files in `app/db/models`, Alembic can autogenerate some migration files.
Trigger this by running:

```bash
alembic revision --autogenerate -m "<message>"
# where message is something like: "Add owner_user_id to workout_types"
```

Alembic will create a new file in `alembic/versions` named something like `9883c28f3b21_add_owner_user_id_to_workout_types.py`.
In that file will be an `upgrade` and a `downgrade` migration; be sure to look these over before committing, but so far I haven't found anything that needs modifying.

These migrations **are not automatically run**; that is to say that your database won't reflect these changes until you explicity run the migration.
To do this, either tear down the database (`./scripts/stop-local-db.sh`) or run `alembic upgrade head`.
