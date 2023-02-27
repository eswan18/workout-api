from uuid import UUID

from sqlalchemy.sql import delete
from sqlalchemy.orm import sessionmaker, Session

from .models import Exercise, ExerciseType, Workout, WorkoutType, User


def recursive_hard_delete(
    user: User | UUID, session_factory: sessionmaker[Session]
) -> int:
    """
    Hard delete everything associated with a user or a user ID.
    """
    with session_factory(expire_on_commit=False) as session:
        if isinstance(user, UUID):
            user_id = user
        else:
            user_id = user.id

        # Order matters -- we need to delete tables with foreign keys first.
        stmts = [
            delete(Exercise).where(Exercise.user_id == user_id),
            delete(ExerciseType).where(ExerciseType.owner_user_id == user_id),
            delete(Workout).where(Workout.user_id == user_id),
            delete(WorkoutType).where(WorkoutType.owner_user_id == user_id),
            delete(User).where(User.id == user_id),
        ]
        rowcount = 0
        for stmt in stmts:
            result = session.execute(stmt)
            session.commit()
            nrows: int = result.rowcount  # type: ignore  # (this seems to work)
            rowcount += nrows
        return rowcount
