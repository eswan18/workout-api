from app.db import User, get_session_factory_sync

session_factory = get_session_factory_sync(echo=False)

erin_quinn = User(
    id="ddf909e8-1ef9-4cdc-8476-732137a352d8",
    email="dummyuser@example.com",
    pw_hash="1234",
)

with session_factory() as session:
    print("Users...")
    print("- Adding user 'Erin Quinn'")
    session.add(erin_quinn)
    session.commit()
    print("...committed")
