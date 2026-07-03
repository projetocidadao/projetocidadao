"""fix_denuncia_status_enum_name

Rename enum status_denuncia -> status_denuncia_enum (alinhamento com model).

Revision ID: 20260703_0400_enum_rename
Revises: 20260703_0300_polish
Create Date: 2026-07-03 04:00:00.000000
"""
from alembic import op

revision = '20260703_0400_enum_rename'
down_revision = '20260703_0300_polish'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Renomeia o enum type no Postgres
    op.execute('ALTER TYPE status_denuncia RENAME TO status_denuncia_enum')


def downgrade() -> None:
    op.execute('ALTER TYPE status_denuncia_enum RENAME TO status_denuncia')
