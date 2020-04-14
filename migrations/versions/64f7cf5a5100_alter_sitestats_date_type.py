"""alter sitestats date type

Revision ID: 64f7cf5a5100
Revises: ca049d392f8e
Create Date: 2020-04-14 14:40:34.113189

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '64f7cf5a5100'
down_revision = 'ca049d392f8e'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "SiteStats", "date", type_=sa.Date, nullable=False
    )


def downgrade():
    op.alter_column(
        "SiteStats", "date", type_=sa.String(32), nullable=False
    )
