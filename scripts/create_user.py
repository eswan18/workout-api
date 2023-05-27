import sys

from app.db.models import User
from app.db.database import get_session_factory_sync
from app.v1.auth import hash_pw

session_factory = get_session_factory_sync()


username, password = sys.argv[1:]
hashed_pw = hash_pw(username, password)

with session_factory() as session:
    user = User(email=username, pw_hash=hashed_pw)
    session.add(user)
    session.commit()
