"""polish_schema_final

Revision ID: 20260703_0300_polish
Revises: 20260703_0230_cidadao
Create Date: 2026-07-03 03:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '20260703_0300_polish'
down_revision: Union[str, None] = '20260703_0230_cidadao'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # comentarios.conteudo: tornar NOT NULL (model pede)
    op.alter_column('comentarios', 'conteudo',
        existing_type=sa.Text(),
        nullable=False
    )

    # faros: adicionar indice em severidade (model pede)
    op.create_index('ix_faros_severidade', 'faros', ['severidade'])


def downgrade() -> None:
    op.drop_index('ix_faros_severidade', table_name='faros')
    op.alter_column('comentarios', 'conteudo',
        existing_type=sa.Text(),
        nullable=True
    )
