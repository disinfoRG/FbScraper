"""add column created at

Revision ID: e15c209c1566
Revises: 6924196dcf9f
Create Date: 2020-02-25 16:09:51.155893

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e15c209c1566"
down_revision = "6924196dcf9f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "Article", sa.Column("created_at", sa.Integer, default=0, nullable=False)
    )


def downgrade():
    op.drop_column("Article", "created_at")
