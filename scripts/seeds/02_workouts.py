from app.db import Workout, get_session_factory_sync


session_factory = get_session_factory_sync(echo=False)


workouts = [
    # Pull day by Erin.
    Workout(
        id="a8d26bbc-c6af-4d85-b019-82096b1a21af",
        start_time="2022-01-01 00:00:00",
        end_time="2022-01-01 01:00:00",
        status="completed",
        workout_type_id="72c29956-f71a-4e6a-b8e2-d6ea2008ed35",
        user_id="ddf909e8-1ef9-4cdc-8476-732137a352d8",
    ),
    # Push day by Erin.
    Workout(
        id="6c4f419a-5931-4b8f-861e-c4866bbf63fd",
        start_time="2022-01-02 00:00:00",
        end_time=None,
        status="paused",
        workout_type_id="a4f69cd3-12ba-42ec-8ffc-b03a167f489e",
        user_id="ddf909e8-1ef9-4cdc-8476-732137a352d8",
    ),
]


with session_factory() as session:
    print("Workouts...")
    for wkt in workouts:
        print(f"- Adding workout '{wkt.id}'")
        session.add(wkt)
    session.commit()
    print("...committed")
