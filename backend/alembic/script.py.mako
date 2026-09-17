"""Mako template for alembic."""

<%!
import re
%>

# Create migration

## Revisions section

# Revision ID: ${up_revision}
# Revises: ${down_revision | comma,n}
# Create Date: ${create_date}

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
