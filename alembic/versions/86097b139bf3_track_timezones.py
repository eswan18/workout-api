"""Track timezones

Revision ID: 86097b139bf3
Revises: 10eafeaba0d6
Create Date: 2023-02-12 17:52:57.751173

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "86097b139bf3"
down_revision = "10eafeaba0d6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ethan wrote these manually, autogeneration didn't work.
    # This alters all the datetime columns in the db to have timezones.
    op.alter_column(
        "sets", "start_time", type_=postgresql.TIMESTAMP(timezone=True),
    )
    op.alter_column(
        "workouts", "start_time", type_=postgresql.TIMESTAMP(timezone=True),
    )
    op.alter_column(
        "workouts", "end_time", type_=postgresql.TIMESTAMP(timezone=True),
    )


def downgrade() -> None:
    # Ethan wrote these manually, autogeneration didn't work.
    op.alter_column(
        "workouts", "end_time", type_=postgresql.TIMESTAMP(timezone=False),
    )
    op.alter_column(
        "workouts", "start_time", type_=postgresql.TIMESTAMP(timezone=False),
    )
    op.alter_column(
        "sets", "start_time", type_=postgresql.TIMESTAMP(timezone=False),
    )