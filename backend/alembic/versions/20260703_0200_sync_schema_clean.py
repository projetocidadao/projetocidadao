"""sync_schema_with_models_clean

Revision ID: 20260703_0200_clean
Revises: 084040312b01
Create Date: 2026-07-03 02:35:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '20260703_0200_clean'
down_revision: Union[str, None] = '084040312b01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === NOTIFICACOES ===
    # Remover colunas nao usadas
    op.drop_column('notificacoes', 'data_leitura')
    op.drop_column('notificacoes', 'updated_at')
    op.drop_column('notificacoes', 'mensagem')

    # === PROGRESSOS ===
    # Alterar tipo da coluna percentual
    op.alter_column(
        'progressos', 'percentual',
        existing_type=sa.INTEGER(),
        type_=sa.Float(),
        existing_nullable=False,
        postgresql_using='percentual::double precision'
    )
    op.drop_column('progressos', 'data_conclusao')
    op.drop_column('progressos', 'pontos_ganhos')

    # === USUARIOS ===
    # Mudar biografia de VARCHAR(500) para Text
    op.alter_column(
        'usuarios', 'biografia',
        existing_type=sa.VARCHAR(length=500),
        type_=sa.Text(),
        existing_nullable=True,
    )
    # Remover coluna bio (substituida por biografia)
    op.drop_column('usuarios', 'bio')

    # === VOTOS ===
    # Remover colunas nao usadas
    op.drop_column('votos', 'pontos')
    op.drop_column('votos', 'apoio')
    op.drop_column('votos', 'updated_at')


def downgrade() -> None:
    # === VOTOS ===
    op.add_column('votos', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('votos', sa.Column('apoio', sa.Boolean(), nullable=True))
    op.add_column('votos', sa.Column('pontos', sa.Integer(), nullable=True))

    # === USUARIOS ===
    op.add_column('usuarios', sa.Column('bio', sa.VARCHAR(length=500), nullable=True))
    op.alter_column(
        'usuarios', 'biografia',
        existing_type=sa.Text(),
        type_=sa.VARCHAR(length=500),
        existing_nullable=True,
    )

    # === PROGRESSOS ===
    op.add_column('progressos', sa.Column('pontos_ganhos', sa.Integer(), nullable=True))
    op.add_column('progressos', sa.Column('data_conclusao', sa.DateTime(timezone=True), nullable=True))
    op.alter_column(
        'progressos', 'percentual',
        existing_type=sa.Float(),
        type_=sa.INTEGER(),
        existing_nullable=False,
    )

    # === NOTIFICACOES ===
    op.add_column('notificacoes', sa.Column('mensagem', sa.Text(), nullable=True))
    op.add_column('notificacoes', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('notificacoes', sa.Column('data_leitura', sa.DateTime(timezone=True), nullable=True))

