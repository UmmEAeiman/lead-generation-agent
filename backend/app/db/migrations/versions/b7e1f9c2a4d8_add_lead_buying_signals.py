"""add lead buying_signals

Revision ID: b7e1f9c2a4d8
Revises: ee86d05a402d
Create Date: 2026-10-10 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = 'b7e1f9c2a4d8'
down_revision: str | None = 'ee86d05a402d'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table('leads', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'buying_signals',
                sa.JSON(),
                nullable=False,
                server_default=sa.text("'[]'"),
            )
        )


def downgrade() -> None:
    with op.batch_alter_table('leads', schema=None) as batch_op:
        batch_op.drop_column('buying_signals')
