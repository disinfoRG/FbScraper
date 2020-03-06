"""refactor article type enum

Revision ID: a5d3cdb5892e
Revises: e15c209c1566
Create Date: 2020-02-25 17:37:49.602606

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a5d3cdb5892e"
down_revision = "e15c209c1566"
branch_labels = None
depends_on = None


def upgrade():
    article_type = sa.dialects.mysql.ENUM("FBPost", "FBComment")
    op.alter_column(
        "Article", "article_type", nullable=False, existing_type=article_type
    )


def downgrade():
    article_type = sa.dialects.mysql.ENUM(
        "Article", "FBPost", "FBComment", "PTT", "Dcard"
    )
    op.alter_column(
        "Article", "article_type", nullable=False, existing_type=article_type
    )
