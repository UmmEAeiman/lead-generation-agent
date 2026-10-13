"""add run_id to leads and outreach

Revision ID: c3f9a1d2b5e7
Revises: b7e1f9c2a4d8
Create Date: 2026-10-13 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = 'c3f9a1d2b5e7'
down_revision: str | None = 'b7e1f9c2a4d8'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table('leads', schema=None) as batch_op:
        batch_op.add_column(sa.Column('run_id', sa.String(length=64), nullable=True))
        batch_op.create_index('ix_leads_run_id', ['run_id'], unique=False)

    with op.batch_alter_table('outreach', schema=None) as batch_op:
        batch_op.add_column(sa.Column('run_id', sa.String(length=64), nullable=True))
        batch_op.create_index('ix_outreach_run_id', ['run_id'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('outreach', schema=None) as batch_op:
        batch_op.drop_index('ix_outreach_run_id')
        batch_op.drop_column('run_id')

    with op.batch_alter_table('leads', schema=None) as batch_op:
        batch_op.drop_index('ix_leads_run_id')
        batch_op.drop_column('run_id')
