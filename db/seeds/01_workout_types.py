from uuid import UUID

from app.db import WorkoutType, get_session_factory_sync

session_factory = get_session_factory_sync(echo=False)

workout_types = [
    # A public workout with no parent.
    WorkoutType(
        id=UUID("3d531b3b-907f-488b-b2b6-ad3e541d08fd"),
        name="Upper Body",
        notes="Upper body exercises -- a broad category",
        parent_workout_type_id=None,
        owner_user_id=None,
    ),
    # Some public workouts with parents.
    WorkoutType(
        id=UUID("72c29956-f71a-4e6a-b8e2-d6ea2008ed35"),
        name="Pull Day",
        notes="Biceps and upper back exercises",
        parent_workout_type_id="3d531b3b-907f-488b-b2b6-ad3e541d08fd",
        owner_user_id=None,
    ),
    WorkoutType(
        id=UUID("a4f69cd3-12ba-42ec-8ffc-b03a167f489e"),
        name="Push Day",
        notes="Chest, shoulders, and triceps exercises; public",
        parent_workout_type_id="3d531b3b-907f-488b-b2b6-ad3e541d08fd",
        owner_user_id=None,
    ),
    # A workout owned by a particular user that's a child of a public workout.
    WorkoutType(
        id=UUID("463b07e1-4185-4a8f-8b59-71192dc141c4"),
        name="Dumbbells for Erin",
        notes="A personal dumbbell workout just for Erin",
        parent_workout_type_id="3d531b3b-907f-488b-b2b6-ad3e541d08fd",
        owner_user_id="ddf909e8-1ef9-4cdc-8476-732137a352d8",
    ),
]

with session_factory() as session:
    print("Workout types...")
    for wt in workout_types:
        print(f"- Adding workout type '{wt.name}'")
        session.add(wt)
    session.commit()
    print("...committed")
