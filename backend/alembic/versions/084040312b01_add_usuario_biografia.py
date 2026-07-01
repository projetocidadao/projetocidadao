"""add_usuario_biografia"""
from alembic import op
import sqlalchemy as sa

revision = '084040312b01'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('usuarios', sa.Column('biografia', sa.String(500), nullable=True))
    op.add_column('usuarios', sa.Column('data_primeira_contribuicao', sa.DateTime(timezone=True), nullable=True))
    op.add_column('usuarios', sa.Column('apto_a_criar', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('usuarios', sa.Column('consentimento_lgpd', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('usuarios', sa.Column('data_consentimento', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('usuarios', 'data_consentimento')
    op.drop_column('usuarios', 'consentimento_lgpd')
    op.drop_column('usuarios', 'apto_a_criar')
    op.drop_column('usuarios', 'data_primeira_contribuicao')
    op.drop_column('usuarios', 'biografia')
