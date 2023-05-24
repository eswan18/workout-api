from uuid import UUID

from app.db import Exercise, get_session_factory_sync


session_factory = get_session_factory_sync(echo=False)


exercises = [
    # Erin did pull day...
    # Two sets of bicep curls.
    Exercise(
        id=UUID("a8d26bbc-c6af-4d85-b019-82096b1a21af"),
        start_time="2022-01-01 00:00:00",
        weight=35,
        weight_unit="lbs",
        reps=8,
        seconds=None,
        notes=None,
        exercise_type_id=UUID("8278d21c-1ffa-4dbf-b5b0-070cdb7824cd"),
        workout_id="a8d26bbc-c6af-4d85-b019-82096b1a21af",
        user_id="ddf909e8-1ef9-4cdc-8476-732137a352d8",
    ),
    Exercise(
        id=UUID("14b11dc1-c14f-4768-8d97-98a33a613c01"),
        start_time="2022-01-01 00:10:10",
        weight=35,
        weight_unit="lbs",
        reps=6,
        seconds=None,
        notes="That was a tough one, failed early.",
        exercise_type_id=UUID("8278d21c-1ffa-4dbf-b5b0-070cdb7824cd"),
        workout_id=UUID("a8d26bbc-c6af-4d85-b019-82096b1a21af"),
        user_id=UUID("ddf909e8-1ef9-4cdc-8476-732137a352d8"),
    ),
    # Two sets of seated rows.
    Exercise(
        id=UUID("777a333b-9461-4ea4-9543-f548af86c02a"),
        start_time="2022-01-01 00:18:31",
        weight=70,
        weight_unit="lbs",
        reps=9,
        seconds=None,
        notes=None,
        exercise_type_id=UUID("5d4d6ef0-5e14-4506-8525-87d3b1903568"),
        workout_id=UUID("a8d26bbc-c6af-4d85-b019-82096b1a21af"),
        user_id=UUID("ddf909e8-1ef9-4cdc-8476-732137a352d8"),
    ),
    Exercise(
        id=UUID("a9228bd9-aa6b-474e-b78a-5cceb5cfa14c"),
        start_time="2022-01-01 00:21:11",
        weight=70,
        weight_unit="lbs",
        reps=9,
        seconds=None,
        notes=None,
        exercise_type_id=UUID("5d4d6ef0-5e14-4506-8525-87d3b1903568"),
        workout_id=UUID("a8d26bbc-c6af-4d85-b019-82096b1a21af"),
        user_id=UUID("ddf909e8-1ef9-4cdc-8476-732137a352d8"),
    ),
]

with session_factory() as session:
    print("Exercises...")
    for ex in exercises:
        print(f"- Adding exercise '{ex.id}'")
        session.add(ex)
    session.commit()
    print("...committed")
