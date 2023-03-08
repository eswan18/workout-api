from app.db import get_session_factory_sync, ExerciseType


session_factory = get_session_factory_sync(echo=False)


exercise_types = [
    # Public exercise types.
    ExerciseType(
        id="8278d21c-1ffa-4dbf-b5b0-070cdb7824cd",
        name="Bicep Curls",
        number_of_weights=2,
        notes=None,
        owner_user_id=None,
    ),
    ExerciseType(
        id="5d4d6ef0-5e14-4506-8525-87d3b1903568",
        name="Seated rows",
        number_of_weights=1,
        notes="(machine)",
        owner_user_id=None,
    ),
    ExerciseType(
        id="1624bfc4-e191-49c7-8173-118058570ac0",
        name="Barbell Squats",
        number_of_weights=1,
        notes="Just the normal ones, not front squats",
        owner_user_id=None,
    ),
    ExerciseType(
        id="bef96a30-3dd5-4c94-abbb-e822301e7083",
        name="Planks",
        number_of_weights=0,
        notes="This is one where we keep track of seconds not reps",
        owner_user_id=None,
    ),
    # An exercise type owned by a specific user.
    ExerciseType(
        id="feb588b5-e86b-4269-8121-475682df2830",
        name="Erin's Deadlift",
        number_of_weights=0,
        notes="Only dummy account knows this secret exercise",
        owner_user_id="ddf909e8-1ef9-4cdc-8476-732137a352d8",
    ),
]


with session_factory() as session:
    print("Exercise Types...")
    for ex_tp in exercise_types:
        print(f"- Adding exercise_type '{ex_tp.name}'")
        session.add(ex_tp)
    session.commit()
    print("...committed")
