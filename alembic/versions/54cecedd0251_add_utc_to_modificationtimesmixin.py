"""Add UTC to ModificationTimesMixin

Revision ID: 54cecedd0251
Revises: 3c91362590bc
Create Date: 2023-02-13 14:19:20.372072

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "54cecedd0251"
down_revision = "3c91362590bc"
branch_labels = None
depends_on = None


tables = ["exercise_types", "sets", "workout_types", "workouts", "users"]
columns = ["created_at", "updated_at"]


def upgrade() -> None:
    # Ethan wrote this by hand.
    for table in tables:
        for column in columns:
            op.alter_column(
                table,
                column,
                server_default=sa.text("timezone('UTC', CURRENT_TIMESTAMP)"),
            )


def downgrade() -> None:
    # Ethan wrote this by hand.
    for table in tables:
        for column in columns:
            op.alter_column(
                table,
                column,
                server_default=sa.text("now()"),
            )
