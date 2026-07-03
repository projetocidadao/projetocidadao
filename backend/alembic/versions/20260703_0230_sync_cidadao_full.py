"""sync_schema_cidadao_full

Revision ID: 20260703_0230_cidadao
Revises: 20260703_0200_clean
Create Date: 2026-07-03 02:38:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '20260703_0230_cidadao'
down_revision: Union[str, None] = '20260703_0200_clean'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === ANEXOS ===
    op.add_column('anexos', sa.Column('descricao', sa.String(length=300), nullable=True))
    op.drop_index('ix_anexos_id', table_name='anexos')

    # === AREAS ===
    op.drop_index('ix_areas_id', table_name='areas')

    # === COMENTARIOS ===
    op.add_column('comentarios', sa.Column('conteudo', sa.Text(), nullable=True))
    op.alter_column('comentarios', 'autor_id', existing_type=sa.INTEGER(), nullable=True)
    op.drop_index('ix_comentarios_autor_id', table_name='comentarios')
    op.drop_index('ix_comentarios_id', table_name='comentarios')
    op.drop_index('ix_comentarios_parent_id', table_name='comentarios')
    op.drop_constraint('comentarios_autor_id_fkey', 'comentarios', type_='foreignkey')
    op.create_foreign_key('comentarios_autor_id_fkey', 'comentarios', 'usuarios', ['autor_id'], ['id'], ondelete='SET NULL')
    op.drop_column('comentarios', 'editado')
    op.drop_column('comentarios', 'texto')

    # === CURSOS ===
    op.drop_index('ix_cursos_id', table_name='cursos')
    op.create_index('ix_cursos_status', 'cursos', ['status'])

    # === DENUNCIAS ===
    op.alter_column('denuncias', 'categoria',
        existing_type=postgresql.ENUM('saude', 'educacao', 'alimentacao', 'transporte', 'seguranca', 'saneamento', 'financas', 'meio_ambiente', 'cultura', 'outro', name='categoria_denuncia'),
        type_=sa.String(length=100),
        existing_nullable=False,
        postgresql_using='categoria::text'
    )
    # NOTA: enum status_denuncia_enum nao eh usado - manter ENUM antigo
    op.drop_index('ix_denuncias_id', table_name='denuncias')
    op.create_index('ix_denuncias_canal_destino', 'denuncias', ['canal_destino'])
    op.create_index('ix_denuncias_created_at', 'denuncias', ['created_at'])
    op.create_index('ix_denuncias_votos', 'denuncias', ['votos'])
    op.drop_constraint('denuncias_area_id_fkey', 'denuncias', type_='foreignkey')
    op.create_foreign_key('denuncias_area_id_fkey', 'denuncias', 'areas', ['area_id'], ['id'])

    # === CRIAR ENUM severidade_faro (necessario antes de usar) ===
    severidade_faro = postgresql.ENUM('BAIXA', 'MEDIA', 'ALTA', 'CRITICA', name='severidade_faro')
    severidade_faro.create(op.get_bind())

    # === FAROS === (cuidado: remover default antes, recriar depois) ===
    op.drop_column('faros', 'severidade')
    op.add_column('faros', sa.Column('severidade', postgresql.ENUM('BAIXA', 'MEDIA', 'ALTA', 'CRITICA', name='severidade_faro', create_type=False), nullable=False, server_default='MEDIA'))
    op.drop_index('ix_faros_id', table_name='faros')
    op.drop_index('ix_faros_tipo_entidade', table_name='faros')

        # === NOTIFICACOES ===
    op.add_column('notificacoes', sa.Column('conteudo', sa.Text(), nullable=True))
    op.alter_column('notificacoes', 'tipo',
        existing_type=postgresql.ENUM('denuncia_criada', 'denuncia_atualizada', 'comentario_novo', 'curso_concluido', 'farejador_alerta', 'sistema', name='tipo_notificacao'),
        type_=sa.String(length=50),
        existing_nullable=False,
        postgresql_using='tipo::text'
    )
    op.drop_index('ix_notificacoes_id', table_name='notificacoes')
    op.drop_index('ix_notificacoes_lida', table_name='notificacoes')
    op.create_index('ix_notificacoes_tipo', 'notificacoes', ['tipo'])

    # === PROGRESSOS ===
    op.drop_index('ix_progressos_id', table_name='progressos')
    op.drop_constraint('uq_progresso_usuario_curso', 'progressos', type_='unique')

    # === USUARIOS ===
    op.drop_index('ix_usuarios_id', table_name='usuarios')
    op.create_index('ix_usuarios_role', 'usuarios', ['role'])

    # === VOTOS ===
    op.drop_index('ix_votos_id', table_name='votos')
    op.drop_constraint('uq_voto_usuario_denuncia', 'votos', type_='unique')
    op.create_index('ix_votos_denuncia_id', 'votos', ['denuncia_id'])
    op.create_index('ix_votos_usuario_id', 'votos', ['usuario_id'])


def downgrade() -> None:
    pass  # reversivel manualmente se necessario
