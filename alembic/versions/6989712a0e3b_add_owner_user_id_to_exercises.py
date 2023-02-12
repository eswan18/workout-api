"""Add owner_user_id to exercises

Revision ID: 6989712a0e3b
Revises: 9883c28f3b21
Create Date: 2023-02-11 21:56:38.009488

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "6989712a0e3b"
down_revision = "9883c28f3b21"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "exercises",
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(None, "exercises", "users", ["owner_user_id"], ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "exercises", type_="foreignkey")
    op.drop_column("exercises", "owner_user_id")
    # ### end Alembic commands ###
