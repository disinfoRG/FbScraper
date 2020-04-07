"""add stats table

Revision ID: ca049d392f8e
Revises: a5d3cdb5892e
Create Date: 2020-04-07 18:41:54.123762

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca049d392f8e'
down_revision = 'a5d3cdb5892e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "SiteStats",
        sa.Column("site_id", sa.Integer, nullable=False),
        sa.Column("date", sa.String(32), nullable=False),
        sa.Column("new_article_count", sa.Integer),
        sa.Column("updated_article_count", sa.Integer),
        sa.PrimaryKeyConstraint("site_id", "date", name="pk_SiteStats"),
    )


def downgrade():
    op.drop_table("SiteStats")
