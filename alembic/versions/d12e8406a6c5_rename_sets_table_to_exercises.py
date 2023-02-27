"""Rename sets table to exercises

Revision ID: d12e8406a6c5
Revises: 54cecedd0251
Create Date: 2023-02-27 08:09:33.529337

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d12e8406a6c5"
down_revision = "54cecedd0251"
branch_labels = None
depends_on = None

constraint_name_changes = [
    ("sets_exercise_type_id_fkey", "exercises_exercise_type_id_fkey"),
    ("sets_user_id_fkey", "exercises_user_id_fkey"),
    ("sets_workout_id_fkey", "exercises_workout_id_fkey"),
]
index_name_change = ("sets_pkey", "exercises_pkey")


def upgrade() -> None:
    # Written by Ethan
    op.rename_table("sets", "exercises")
    for old_name, new_name in constraint_name_changes:
        rename_clause = f"RENAME CONSTRAINT {old_name} TO {new_name}"
        stmt = sa.text(f"ALTER TABLE EXERCISES {rename_clause}")
        op.execute(stmt)
    stmt = f"ALTER INDEX {index_name_change[0]} RENAME TO {index_name_change[1]}"
    op.execute(stmt)


def downgrade() -> None:
    # Written by Ethan
    stmt = f"ALTER INDEX {index_name_change[1]} RENAME TO {index_name_change[0]}"
    op.execute(stmt)
    for new_name, old_name in reversed(constraint_name_changes):
        rename_clause = f"RENAME CONSTRAINT {old_name} TO {new_name}"
        stmt = sa.text(f"ALTER TABLE EXERCISES {rename_clause}")
        op.execute(stmt)
    op.rename_table("exercises", "sets")
